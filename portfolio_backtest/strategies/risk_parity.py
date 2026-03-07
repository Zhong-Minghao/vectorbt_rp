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
        risk_free_rate: float = 0.0
    ):
        """
        初始化风险平价策略

        Args:
            lookback: 协方差矩阵回看窗口（天数）
            rebalance_freq: 调仓频率 ('ME'=月末, 'QE'=季末, 'MS'=月初等)
            risk_free_rate: 无风险利率（暂未使用）
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

    def _solve_risk_parity_weights(self, cov_mat: np.ndarray) -> np.ndarray:
        """
        求解风险平价权重 - 使用优化算法，结果稳定可复现

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
            raise ValueError(f'风险平价优化失败: {result.message}')

        return result.x

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

        # 直接遍历调仓日期，而不是所有交易日
        for dt in rebalance_dates:

            # 确保有足够回看窗口
            if returns.loc[:dt].shape[0] < self.lookback:
                continue

            # 获取窗口期收益率
            window_ret = returns.loc[:dt].tail(self.lookback)

            # 计算协方差矩阵
            cov_mat = window_ret.cov().values

            # 求解风险平价权重
            try:
                w = self._solve_risk_parity_weights(cov_mat)
                weights_list.append(w)
                weight_dates.append(dt)
            except ValueError:
                # 如果优化失败，跳过该日期
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
