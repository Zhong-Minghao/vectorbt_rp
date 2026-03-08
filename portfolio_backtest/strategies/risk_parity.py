"""
风险平价策略实现
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Optional
from .base import BaseStrategy


class RiskParityStrategy(BaseStrategy):
    """
    风险平价策略

    目标：使得每个资产对组合的风险贡献相等
    """

    def __init__(
        self,
        lookback: int = 60,
        rebalance_freq: str = 'ME',
        risk_free_rate: float = 0.0,
        method: str = 'SLSQP',
        compare_methods: bool = False
    ):
        """
        初始化风险平价策略

        Args:
            lookback: 协方差矩阵回看窗口（天数）
            rebalance_freq: 调仓频率 ('ME'=月末, 'QE'=季末, 'MS'=月初等)
            risk_free_rate: 无风险利率（暂未使用）
            method: 优化方法 ('SLSQP' 或 'CDD')
            compare_methods: 是否同时输出两种方法的结果用于验证
        """
        super().__init__(
            name="Risk Parity",
            lookback=lookback,
            rebalance_freq=rebalance_freq,
            risk_free_rate=risk_free_rate
        )
        self.lookback = lookback
        self.rebalance_freq = rebalance_freq
        self.risk_free_rate = risk_free_rate
        self.method = method
        self.compare_methods = compare_methods

    def _solve_risk_parity_weights_slssp(self, cov_mat: np.ndarray) -> np.ndarray:
        """
        使用SLSQP算法求解风险平价权重 - 使用优化算法，结果稳定可复现

        Args:
            cov_mat: 协方差矩阵

        Returns:
            归一化的权重数组
        """
        n = cov_mat.shape[0]

        # 目标函数：最小化风险贡献的方差
        def risk_parity_objective(weights):
            """使所有资产的风险贡献相等"""
            # 组合方差
            port_var = weights @ cov_mat @ weights
            # 边际风险贡献
            marginal_contrib = cov_mat @ weights
            # 风险贡献
            risk_contrib = weights * marginal_contrib
            # 目标：风险贡献应该相等，即方差为0
            # 使用相对风险贡献
            relative_rc = risk_contrib / port_var
            target_rc = 1.0 / n
            return np.sum((relative_rc - target_rc) ** 2)

        # 约束条件：权重和为1
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        # 边界：权重在[0, 1]之间
        bounds = [(0, 1) for _ in range(n)]
        # 初始值：等权重
        x0 = np.ones(n) / n
        x0 = np.random.dirichlet(np.ones(n))

        # 使用SLSQP优化算法
        result = minimize(
            risk_parity_objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'ftol': 1e-15, 'maxiter': 1000}
        )

        if not result.success:
            raise ValueError(f'风险平价SLSQP优化失败: {result.message}')

        return result.x

    def _solve_risk_parity_weights_cdd(self, cov_mat, max_iter=1000, tol=1e-10):

        n = cov_mat.shape[0]

        x = np.ones(n)

        risk_budget = np.ones(n) / n

        for _ in range(max_iter):

            x_old = x.copy()

            for i in range(n):

                a = cov_mat[i, i]

                b = cov_mat[i] @ x - a * x[i]

                c = risk_budget[i]

                x[i] = (-b + np.sqrt(b*b + 4*a*c)) / (2*a)

            if np.linalg.norm(x - x_old) < tol:
                break

        w = x / np.sum(x)

        return w

    def _solve_risk_parity_weights(self, cov_mat: np.ndarray, method: str = 'SLSQP') -> np.ndarray:
        """
        求解风险平价权重 - 支持多种算法

        Args:
            cov_mat: 协方差矩阵
            method: 优化方法 ('SLSQP' 或 'CDD')

        Returns:
            归一化的权重数组
        """
        if method == 'SLSQP':
            return self._solve_risk_parity_weights_slssp(cov_mat)
        elif method == 'CDD':
            return self._solve_risk_parity_weights_cdd(cov_mat)
        else:
            raise ValueError(f'不支持的优化方法: {method}')

    def generate_weights(
        self,
        price_df: pd.DataFrame,
        rebalance_mask: Optional[pd.Series] = None
    ) -> pd.DataFrame:
        """
        生成每个调仓日的风险平价权重

        Args:
            price_df: 日收盘价 DataFrame
            rebalance_mask: 调仓日标记（可选，如不提供则自动生成）

        Returns:
            权重 DataFrame，索引为调仓日，列为资产
        """
        # 验证数据
        price_df = self.validate_data(price_df)

        # 计算收益率
        returns = price_df.pct_change(fill_method=None).dropna()

        # 获取调仓日期（确保这些日期在数据中存在）
        if rebalance_mask is None:
            rebalance_dates = self.get_rebalance_dates(price_df, self.rebalance_freq)
        else:
            # 如果提供了 rebalance_mask，从其中提取调仓日期
            # 确保只返回在 price_df 中存在的日期
            rebalance_dates = price_df.index[rebalance_mask]

        weights_list = []
        weight_dates = []

        # 如果需要对比两种方法，则额外存储对比结果
        self.weights_comparison = {} if self.compare_methods else None

        # 直接遍历调仓日期，而不是所有交易日
        for dt in rebalance_dates:

            # 确保有足够回看窗口
            if returns.loc[:dt].shape[0] < self.lookback:
                continue

            # 获取窗口期收益率
            window_ret = returns.loc[:dt].tail(self.lookback)

            # 计算协方差矩阵, 比pd.cov()更快【20260308】
            cov_mat = np.cov(window_ret.values, rowvar=False)

            # 求解风险平价权重
            try:
                if self.compare_methods:
                    # 同时计算两种方法
                    w_slssp = self._solve_risk_parity_weights(cov_mat, method='SLSQP')
                    w_cdd = self._solve_risk_parity_weights(cov_mat, method='CDD')

                    # 使用选定的方法作为主要结果
                    w = w_slssp if self.method == 'SLSQP' else w_cdd

                    # 存储对比结果
                    self.weights_comparison[dt] = {
                        'SLSQP': w_slssp,
                        'CDD': w_cdd,
                        'diff': np.abs(w_slssp - w_cdd),
                        'max_diff': np.max(np.abs(w_slssp - w_cdd))
                    }
                else:
                    # 只使用选定的方法
                    w = self._solve_risk_parity_weights(cov_mat, method=self.method)

                weights_list.append(w)
                weight_dates.append(dt)
            except ValueError as e:
                # 如果优化失败，跳过该日期
                print(f"警告: {dt} 优化失败 - {e}")
                continue

        weights_df = pd.DataFrame(
            weights_list,
            index=weight_dates,
            columns=price_df.columns
        )

        return weights_df

    def analyze_risk_contributions(
        self,
        weights: np.ndarray,
        cov_matrix: np.ndarray,
        asset_names: list
    ) -> pd.DataFrame:
        """
        分析风险贡献度

        Args:
            weights: 权重数组
            cov_matrix: 协方差矩阵
            asset_names: 资产名称列表

        Returns:
            风险贡献分析 DataFrame
        """
        portfolio_vol = np.sqrt(weights.T @ cov_matrix @ weights)
        risk_contributions = weights * (cov_matrix @ weights) / portfolio_vol
        percentage_rc = risk_contributions / portfolio_vol * 100

        return pd.DataFrame({
            '权重': weights,
            '风险贡献': risk_contributions,
            '风险贡献百分比%': percentage_rc
        }, index=asset_names)

    def print_weights_comparison(self):
        """
        打印SLSQP和CDD两种方法的权重对比结果
        """
        if not self.compare_methods or not self.weights_comparison:
            print("未启用方法对比或没有对比数据")
            return

        print("=" * 80)
        print("风险平价权重对比 (SLSQP vs CDD)")
        print("=" * 80)

        # 按时间排序
        sorted_dates = sorted(self.weights_comparison.keys())

        for dt in sorted_dates:
            comparison = self.weights_comparison[dt]
            print(f"\n日期: {dt}")
            print(f"最大差异: {comparison['max_diff']:.6f}")

            # 创建对比表
            df_comparison = pd.DataFrame({
                'SLSQP': comparison['SLSQP'],
                'CDD': comparison['CDD'],
                '绝对差异': comparison['diff']
            })
            print(df_comparison.to_string())

        # 统计信息
        max_diffs = [comp['max_diff'] for comp in self.weights_comparison.values()]
        print(f"\n统计信息:")
        print(f"平均最大差异: {np.mean(max_diffs):.6f}")
        print(f"最大差异: {np.max(max_diffs):.6f}")
        print(f"最小差异: {np.min(max_diffs):.6f}")
        print("=" * 80)
