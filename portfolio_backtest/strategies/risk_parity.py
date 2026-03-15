"""
风险平价策略实现
"""

import numpy as np
import pandas as pd
from typing import Optional
from .base import BaseStrategy
from ..risk.covariance import CovarianceEstimator
from ..optimizer.optimizers import RiskParityOptimizer


class RiskParityStrategy(BaseStrategy):
    """
    风险平价策略

    目标：使得每个资产对组合的风险贡献按照指定比例分配

    支持：
    - 等风险贡献（默认）：每个资产承担相同的风险
    - 自定义风险预算：指定每个资产的风险贡献目标

    示例：
        # 等风险贡献（默认）
        strategy = RiskParityStrategy(lookback=60)

        # 自定义风险预算
        import numpy as np
        risk_budget = np.array([0.6, 0.4])  # 资产1承担60%风险，资产2承担40%风险
        strategy = RiskParityStrategy(lookback=60, risk_budget=risk_budget)
    """

    def __init__(
        self,
        lookback: int = 60,
        rebalance_freq: str = 'ME',
        risk_free_rate: float = 0.0,
        method: str = 'SLSQP',
        compare_methods: bool = False,
        risk_model: str = 'sample',
        risk_budget: Optional[np.ndarray] = None
    ):
        """
        初始化风险平价策略

        Args:
            lookback: 协方差矩阵回看窗口（天数）
            rebalance_freq: 调仓频率 ('ME'=月末, 'QE'=季末, 'MS'=月初等)
            risk_free_rate: 无风险利率（暂未使用）
            method: 优化方法 ('SLSQP' 或 'CDD')
            compare_methods: 是否同时输出两种方法的结果用于验证
            risk_model: 风险模型类型 ('sample', 'ledoit_wolf', 'oracle_approximating')
            risk_budget: 自定义风险预算（None=等权重，否则指定每个资产的风险贡献目标）
                        例如：np.array([0.6, 0.4]) 表示资产1承担60%风险，资产2承担40%风险
        """
        super().__init__(
            name="Risk Parity",
            lookback=lookback,
            rebalance_freq=rebalance_freq,
            risk_free_rate=risk_free_rate,
            risk_model=risk_model
        )
        self.lookback = lookback
        self.rebalance_freq = rebalance_freq
        self.risk_free_rate = risk_free_rate
        self.method = method
        self.compare_methods = compare_methods
        self.risk_model = risk_model
        self.risk_budget = risk_budget

        # 初始化风险模型和优化器
        self.cov_estimator = CovarianceEstimator(method=risk_model)
        self.optimizer = RiskParityOptimizer(method=method, risk_budget=risk_budget)

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

            # 使用风险模型估计协方差矩阵
            cov_mat = self.cov_estimator.estimate_risk(window_ret)

            # 使用优化器求解权重
            try:
                if self.compare_methods:
                    # 同时计算两种方法
                    optimizer_slssp = RiskParityOptimizer(method='SLSQP')
                    optimizer_cdd = RiskParityOptimizer(method='CDD')

                    w_slssp = optimizer_slssp.optimize(cov_matrix=cov_mat)
                    w_cdd = optimizer_cdd.optimize(cov_matrix=cov_mat)

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
                    w = self.optimizer.optimize(cov_matrix=cov_mat)

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
        # 使用风险模型计算风险贡献
        risk_contrib = self.cov_estimator.calculate_risk_contribution(weights, cov_matrix)
        portfolio_vol = np.sqrt(weights.T @ cov_matrix @ weights)

        # 转换为DataFrame格式
        return pd.DataFrame({
            '权重': weights,
            '风险贡献': risk_contrib,
            '风险贡献百分比%': risk_contrib * 100
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
