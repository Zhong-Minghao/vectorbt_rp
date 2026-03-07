"""
均值方差策略实现
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Optional
from .base import BaseStrategy


class MeanVarianceStrategy(BaseStrategy):
    """
    均值方差策略

    基于 Markowitz 现代投资组合理论
    """

    def __init__(
        self,
        lookback: int = 60,
        rebalance_freq: str = 'ME',
        target_return: Optional[float] = None,
        risk_aversion: float = 1.0,
        weight_bounds: tuple = (0, 1)
    ):
        """
        初始化均值方差策略

        Args:
            lookback: 均值和协方差回看窗口（天数）
            rebalance_freq: 调仓频率
            target_return: 目标收益率（如不提供则优化夏普比率）
            risk_aversion: 风险厌恶系数（用于最大化效用函数）
            weight_bounds: 权重边界
        """
        super().__init__(
            name="Mean Variance",
            lookback=lookback,
            rebalance_freq=rebalance_freq,
            target_return=target_return,
            risk_aversion=risk_aversion,
            weight_bounds=weight_bounds
        )
        self.lookback = lookback
        self.rebalance_freq = rebalance_freq
        self.target_return = target_return
        self.risk_aversion = risk_aversion
        self.weight_bounds = weight_bounds

    def _solve_max_sharpe_weights(
        self,
        mean_returns: np.ndarray,
        cov_mat: np.ndarray,
        risk_free_rate: float = 0.0
    ) -> np.ndarray:
        """
        求解最大化夏普比率的权重

        Args:
            mean_returns: 预期收益率
            cov_mat: 协方差矩阵
            risk_free_rate: 无风险利率

        Returns:
            最优权重
        """
        n = len(mean_returns)

        def neg_sharpe_ratio(weights, mean_returns, cov_mat, risk_free_rate):
            portfolio_return = weights @ mean_returns
            portfolio_vol = np.sqrt(weights @ cov_mat @ weights.T)
            sharpe = (portfolio_return - risk_free_rate) / portfolio_vol
            return -sharpe

        cons = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
        bounds = [self.weight_bounds] * n

        result = minimize(
            neg_sharpe_ratio,
            x0=np.ones(n) / n,
            args=(mean_returns, cov_mat, risk_free_rate),
            method='SLSQP',
            bounds=bounds,
            constraints=cons,
            options={'maxiter': 1000, 'ftol': 1e-14}
        )

        if result.success:
            return result.x
        else:
            # 失败时返回等权重
            return np.ones(n) / n

    def _solve_min_variance_weights(self, cov_mat: np.ndarray) -> np.ndarray:
        """
        求解最小化方差的权重

        Args:
            cov_mat: 协方差矩阵

        Returns:
            最小方差权重
        """
        n = cov_mat.shape[0]

        def portfolio_variance(weights, cov_mat):
            return weights @ cov_mat @ weights.T

        cons = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
        bounds = [self.weight_bounds] * n

        result = minimize(
            portfolio_variance,
            x0=np.ones(n) / n,
            args=(cov_mat,),
            method='SLSQP',
            bounds=bounds,
            constraints=cons,
            options={'maxiter': 1000, 'ftol': 1e-14}
        )

        if result.success:
            return result.x
        else:
            return np.ones(n) / n

    def _solve_target_return_weights(
        self,
        mean_returns: np.ndarray,
        cov_mat: np.ndarray,
        target_return: float
    ) -> np.ndarray:
        """
        求解给定目标收益率下最小方差的权重

        Args:
            mean_returns: 预期收益率
            cov_mat: 协方差矩阵
            target_return: 目标收益率

        Returns:
            最优权重
        """
        n = len(mean_returns)

        def portfolio_variance(weights, cov_mat):
            return weights @ cov_mat @ weights.T

        cons = (
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},  # 权重和为1
            {'type': 'eq', 'fun': lambda w: w @ mean_returns - target_return}  # 目标收益
        )
        bounds = [self.weight_bounds] * n

        result = minimize(
            portfolio_variance,
            x0=np.ones(n) / n,
            args=(cov_mat,),
            method='SLSQP',
            bounds=bounds,
            constraints=cons,
            options={'maxiter': 1000, 'ftol': 1e-14}
        )

        if result.success:
            return result.x
        else:
            return np.ones(n) / n

    def generate_weights(
        self,
        price_df: pd.DataFrame,
        rebalance_mask: Optional[pd.Series] = None
    ) -> pd.DataFrame:
        """
        生成每个调仓日的均值方差权重

        Args:
            price_df: 日收盘价 DataFrame
            rebalance_mask: 调仓日标记（可选）

        Returns:
            权重 DataFrame
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
            # 确保日期在 returns 中存在
            if dt not in returns.index:
                continue

            # 确保有足够回看窗口
            if returns.loc[:dt].shape[0] < self.lookback:
                continue

            # 获取窗口期收益率
            window_ret = returns.loc[:dt].tail(self.lookback)

            # 计算均值和协方差
            mean_returns = window_ret.mean().values * 252  # 年化
            cov_mat = window_ret.cov().values * 252  # 年化

            # 根据参数选择优化目标
            if self.target_return is not None:
                w = self._solve_target_return_weights(mean_returns, cov_mat, self.target_return)
            else:
                # 默认最大化夏普比率
                w = self._solve_max_sharpe_weights(mean_returns, cov_mat)

            weights_list.append(w)
            weight_dates.append(dt)

        weights_df = pd.DataFrame(
            weights_list,
            index=weight_dates,
            columns=price_df.columns
        )

        return weights_df
