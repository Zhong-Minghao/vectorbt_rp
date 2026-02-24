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
        求解风险平价权重

        Args:
            cov_mat: 协方差矩阵

        Returns:
            归一化的权重数组
        """
        n = cov_mat.shape[0]

        # 使用不同的初始值多次尝试
        initial_guesses = [
            np.ones(n) / n,  # 等权重
            np.random.dirichlet(np.ones(n)),  # 随机权重
        ]

        # 对数目标函数
        def portfolio_risk_log(weights, cov):
            port_var = weights @ cov @ weights.T
            marginal_contrib = cov @ weights
            risk_contrib = weights * marginal_contrib
            log_rc = np.log(np.abs(risk_contrib) + 1e-12)
            mean_log_rc = np.mean(log_rc)
            return np.sum((log_rc - mean_log_rc)**2)

        cons = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
        bounds = [(1e-8, 1)] * n

        best_result = None
        best_value = np.inf

        # 多次尝试，选择最好的结果
        for x0 in initial_guesses:
            res = minimize(
                portfolio_risk_log,
                x0,
                args=(cov_mat,),
                method='SLSQP',
                bounds=bounds,
                constraints=cons,
                options={'maxiter': 10000, 'ftol': 1e-14}
            )

            if res.success and res.fun < best_value:
                best_value = res.fun
                best_result = res.x

        # 如果所有尝试都失败，返回基于波动率的简单风险平价权重
        if best_result is None:
            vol = np.sqrt(np.diag(cov_mat))
            inv_vol = 1 / (vol + 1e-12)
            best_result = inv_vol / np.sum(inv_vol)

        return best_result

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

        # 如果没有提供调仓日标记，则生成
        if rebalance_mask is None:
            rebalance_dates = self.get_rebalance_dates(price_df, self.rebalance_freq)
            rebalance_mask = pd.Series(
                price_df.index.isin(rebalance_dates),
                index=price_df.index
            )

        weights_list = []
        weight_dates = []

        for dt in price_df.index:
            if not rebalance_mask.loc[dt]:
                continue

            # 确保有足够回看窗口
            if returns.loc[:dt].shape[0] < self.lookback:
                continue

            # 获取窗口期收益率
            window_ret = returns.loc[:dt].tail(self.lookback)

            # 计算协方差矩阵
            cov_mat = window_ret.cov().values

            # 求解风险平价权重
            w = self._solve_risk_parity_weights(cov_mat)

            weights_list.append(w)
            weight_dates.append(dt)

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
