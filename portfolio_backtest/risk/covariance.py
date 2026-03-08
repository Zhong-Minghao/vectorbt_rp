"""
协方差矩阵估计方法
"""

import numpy as np
import pandas as pd
from typing import Optional, Literal
from .base import BaseRiskModel


class CovarianceEstimator(BaseRiskModel):
    """
    协方差矩阵估计器

    提供多种协方差矩阵估计方法
    """

    def __init__(
        self,
        method: Literal['sample', 'ledoit_wolf', 'oracle_approximating'] = 'sample',
        annualize: bool = False,
        trading_days: int = 252
    ):
        """
        初始化协方差估计器

        Args:
            method: 估计方法 ('sample'=样本协方差, 'ledoit_wolf'=Ledoit-Wolf收缩,
                    'oracle_approximating'=OAS收缩)
            annualize: 是否年化
            trading_days: 年化时的交易日数
        """
        super().__init__(
            name=f"Covariance Estimator ({method})",
            method=method,
            annualize=annualize,
            trading_days=trading_days
        )
        self.method = method
        self.annualize = annualize
        self.trading_days = trading_days

    def estimate_risk(self, returns: pd.DataFrame) -> np.ndarray:
        """
        估计协方差矩阵

        Args:
            returns: 收益率 DataFrame，T x N (T个时间点，N个资产)

        Returns:
            N x N 协方差矩阵
        """
        # 将 DataFrame 转换为 numpy 数组
        ret_values = returns.values if isinstance(returns, pd.DataFrame) else returns

        # 处理缺失值
        if isinstance(returns, pd.DataFrame):
            ret_values = returns.dropna().values
        else:
            # 如果是 numpy 数列，删除包含 NaN 的行
            ret_values = ret_values[~np.isnan(ret_values).any(axis=1)]

        # 计算样本协方差矩阵（更快）
        cov_matrix = np.cov(ret_values, rowvar=False)

        # 根据方法选择不同的估计方式
        if self.method == 'sample':
            pass  # 已经计算了样本协方差
        elif self.method == 'ledoit_wolf':
            cov_matrix = self._ledoit_wolf_shrinkage(ret_values)
        elif self.method == 'oracle_approximating':
            cov_matrix = self._oracle_approximating_shrinkage(ret_values)
        else:
            raise ValueError(f"未知的协方差估计方法: {self.method}")

        # 年化处理
        if self.annualize:
            cov_matrix = cov_matrix * self.trading_days

        return cov_matrix

    def _ledoit_wolf_shrinkage(self, returns: np.ndarray) -> np.ndarray:
        """
        Ledoit-Wolf 收缩估计器

        将样本协方差矩阵向收缩目标（常数相关系数矩阵）收缩

        Args:
            returns: 收益率矩阵 T x N

        Returns:
            收缩后的协方差矩阵
        """
        T, N = returns.shape

        # 样本协方差
        sample_cov = np.cov(returns, rowvar=False)

        # 计算收缩参数
        # 简化版本：使用 Ledoit-Wolf 的解析解
        # 这里实现一个简化版本

        # 计算常数相关系数矩阵作为收缩目标
        var = np.diag(sample_cov)
        mean_var = np.mean(var)
        mean_corr = (np.sum(sample_cov / np.sqrt(var[:, None] * var[None, :])) - N) / (N * (N - 1))
        target = mean_corr * np.sqrt(var[:, None] * var[None, :])
        np.fill_diagonal(target, var)

        # 简化的收缩系数（实际应用中应该使用完整的 Ledoit-Wolf 公式）
        shrinkage = max(0, min(1, (N + 1) / T))

        # 收缩估计
        shrunk_cov = shrinkage * target + (1 - shrinkage) * sample_cov

        return shrunk_cov

    def _oracle_approximating_shrinkage(self, returns: np.ndarray) -> np.ndarray:
        """
        Oracle Approximating Shrinkage (OAS)

        假设数据服从高斯分布的收缩方法

        Args:
            returns: 收益率矩阵 T x N

        Returns:
            收缩后的协方差矩阵
        """
        T, N = returns.shape

        # 样本协方差
        sample_cov = np.cov(returns, rowvar=False)

        # 计算 OAS 收缩系数
        # 这是一个简化版本
        trace = np.trace(sample_cov)
        frobenius = np.sum(sample_cov ** 2)
        shrinkage = min(1, frobenius / (frobenius + trace ** 2))

        # 目标矩阵（单位矩阵的缩放）
        target = (trace / N) * np.eye(N)

        # 收缩估计
        shrunk_cov = shrinkage * target + (1 - shrinkage) * sample_cov

        return shrunk_cov

    def calculate_risk_contribution(
        self,
        weights: np.ndarray,
        cov_matrix: np.ndarray
    ) -> np.ndarray:
        """
        计算风险贡献

        Args:
            weights: 权重向量
            cov_matrix: 协方差矩阵

        Returns:
            各资产的风险贡献
        """
        # 组合方差
        portfolio_var = weights.T @ cov_matrix @ weights
        portfolio_vol = np.sqrt(portfolio_var)

        # 边际风险贡献
        marginal_contrib = cov_matrix @ weights

        # 风险贡献
        risk_contrib = weights * marginal_contrib

        # 归一化为百分比
        percentage_contrib = risk_contrib / portfolio_vol

        return percentage_contrib