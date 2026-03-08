"""
投资组合优化器实现
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Optional, Literal, Union
from .base import BaseOptimizer


class RiskParityOptimizer(BaseOptimizer):
    """
    风险平价优化器

    目标：使得每个资产对组合的风险贡献相等
    """

    def __init__(
        self,
        method: Literal['SLSQP', 'CDD'] = 'SLSQP',
        risk_budget: Optional[np.ndarray] = None,
        weight_bounds: tuple = (0, 1),
        max_iter: int = 1000,
        tol: float = 1e-10
    ):
        """
        初始化风险平价优化器

        Args:
            method: 优化方法 ('SLSQP' 或 'CDD')
            risk_budget: 风险预算（默认等权重）
            weight_bounds: 权重边界
            max_iter: 最大迭代次数（用于CDD）
            tol: 收敛容忍度（用于CDD）
        """
        super().__init__(
            name=f"Risk Parity Optimizer ({method})",
            method=method,
            weight_bounds=weight_bounds,
            max_iter=max_iter,
            tol=tol
        )
        self.method = method
        self.risk_budget = risk_budget
        self.weight_bounds = weight_bounds
        self.max_iter = max_iter
        self.tol = tol

    def optimize(
        self,
        returns: Optional[pd.DataFrame] = None,
        cov_matrix: Optional[np.ndarray] = None,
        mean_returns: Optional[np.ndarray] = None,
        **kwargs
    ) -> np.ndarray:
        """
        优化风险平价组合

        Args:
            returns: 收益率 DataFrame（如果未提供 cov_matrix 则需要）
            cov_matrix: 协方差矩阵
            mean_returns: 未使用
            **kwargs: 其他参数

        Returns:
            最优权重向量
        """
        # 获取协方差矩阵
        if cov_matrix is None:
            if returns is None:
                raise ValueError("必须提供 returns 或 cov_matrix")
            cov_matrix = np.cov(returns.values, rowvar=False)

        # 设置默认风险预算（等权重）
        n = cov_matrix.shape[0]
        if self.risk_budget is None:
            self.risk_budget = np.ones(n) / n

        # 根据方法选择优化算法
        if self.method == 'SLSQP':
            return self._optimize_slssp(cov_matrix)
        elif self.method == 'CDD':
            return self._optimize_cdd(cov_matrix)
        else:
            raise ValueError(f"不支持的优化方法: {self.method}")

    def _optimize_slssp(self, cov_mat: np.ndarray) -> np.ndarray:
        """
        使用SLSQP算法求解风险平价权重

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
            relative_rc = risk_contrib / port_var
            target_rc = self.risk_budget
            return np.sum((relative_rc - target_rc) ** 2)

        # 约束条件：权重和为1
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        # 边界：权重在[0, 1]之间
        bounds = [self.weight_bounds] * n
        # 初始值：随机权重
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

    def _optimize_cdd(self, cov_mat: np.ndarray) -> np.ndarray:
        """
        使用CCD（Cyclical Coordinate Descent）算法求解风险平价权重

        Args:
            cov_mat: 协方差矩阵

        Returns:
            归一化的权重数组
        """
        n = cov_mat.shape[0]
        x = np.ones(n)
        risk_budget = self.risk_budget

        for _ in range(self.max_iter):
            x_old = x.copy()

            for i in range(n):
                a = cov_mat[i, i]
                b = cov_mat[i] @ x - a * x[i]
                c = risk_budget[i]
                x[i] = (-b + np.sqrt(b*b + 4*a*c)) / (2*a)

            if np.linalg.norm(x - x_old) < self.tol:
                break

        w = x / np.sum(x)
        return w


class MeanVarianceOptimizer(BaseOptimizer):
    """
    均值方差优化器

    基于 Markowitz 现代投资组合理论
    """

    def __init__(
        self,
        objective: Literal['max_sharpe', 'min_variance', 'target_return'] = 'max_sharpe',
        target_return: Optional[float] = None,
        risk_free_rate: float = 0.0,
        risk_aversion: float = 1.0,
        weight_bounds: tuple = (0, 1)
    ):
        """
        初始化均值方差优化器

        Args:
            objective: 优化目标 ('max_sharpe', 'min_variance', 'target_return')
            target_return: 目标收益率（仅当objective='target_return'时使用）
            risk_free_rate: 无风险利率
            risk_aversion: 风险厌恶系数
            weight_bounds: 权重边界
        """
        super().__init__(
            name=f"Mean Variance Optimizer ({objective})",
            objective=objective,
            target_return=target_return,
            risk_free_rate=risk_free_rate,
            risk_aversion=risk_aversion,
            weight_bounds=weight_bounds
        )
        self.objective = objective
        self.target_return = target_return
        self.risk_free_rate = risk_free_rate
        self.risk_aversion = risk_aversion
        self.weight_bounds = weight_bounds

    def optimize(
        self,
        returns: Optional[pd.DataFrame] = None,
        cov_matrix: Optional[np.ndarray] = None,
        mean_returns: Optional[np.ndarray] = None,
        **kwargs
    ) -> np.ndarray:
        """
        优化均值方差组合

        Args:
            returns: 收益率 DataFrame（如果未提供 cov_matrix 和 mean_returns 则需要）
            cov_matrix: 协方差矩阵
            mean_returns: 预期收益率
            **kwargs: 其他参数

        Returns:
            最优权重向量
        """
        # 从 returns 计算所需的统计量
        if cov_matrix is None or mean_returns is None:
            if returns is None:
                raise ValueError("必须提供 returns，或者同时提供 cov_matrix 和 mean_returns")
            if mean_returns is None:
                mean_returns = returns.mean().values
            if cov_matrix is None:
                cov_matrix = returns.cov().values

        # 根据目标选择优化方法
        if self.objective == 'max_sharpe':
            return self._optimize_max_sharpe(mean_returns, cov_matrix)
        elif self.objective == 'min_variance':
            return self._optimize_min_variance(cov_matrix)
        elif self.objective == 'target_return':
            if self.target_return is None:
                raise ValueError("target_return 模式需要指定 target_return 参数")
            return self._optimize_target_return(mean_returns, cov_matrix, self.target_return)
        else:
            raise ValueError(f"不支持的优化目标: {self.objective}")

    def _optimize_max_sharpe(
        self,
        mean_returns: np.ndarray,
        cov_mat: np.ndarray
    ) -> np.ndarray:
        """
        求解最大化夏普比率的权重

        Args:
            mean_returns: 预期收益率
            cov_mat: 协方差矩阵

        Returns:
            最优权重
        """
        n = len(mean_returns)

        def neg_sharpe_ratio(weights):
            portfolio_return = weights @ mean_returns
            portfolio_vol = np.sqrt(weights @ cov_mat @ weights.T)
            sharpe = (portfolio_return - self.risk_free_rate) / portfolio_vol
            return -sharpe

        cons = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
        bounds = [self.weight_bounds] * n

        result = minimize(
            neg_sharpe_ratio,
            x0=np.ones(n) / n,
            method='SLSQP',
            bounds=bounds,
            constraints=cons,
            options={'maxiter': 1000, 'ftol': 1e-14}
        )

        if result.success:
            return result.x
        else:
            return np.ones(n) / n

    def _optimize_min_variance(self, cov_mat: np.ndarray) -> np.ndarray:
        """
        求解最小化方差的权重

        Args:
            cov_mat: 协方差矩阵

        Returns:
            最小方差权重
        """
        n = cov_mat.shape[0]

        def portfolio_variance(weights):
            return weights @ cov_mat @ weights.T

        cons = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
        bounds = [self.weight_bounds] * n

        result = minimize(
            portfolio_variance,
            x0=np.ones(n) / n,
            method='SLSQP',
            bounds=bounds,
            constraints=cons,
            options={'maxiter': 1000, 'ftol': 1e-14}
        )

        if result.success:
            return result.x
        else:
            return np.ones(n) / n

    def _optimize_target_return(
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

        def portfolio_variance(weights):
            return weights @ cov_mat @ weights.T

        cons = (
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
            {'type': 'eq', 'fun': lambda w: w @ mean_returns - target_return}
        )
        bounds = [self.weight_bounds] * n

        result = minimize(
            portfolio_variance,
            x0=np.ones(n) / n,
            method='SLSQP',
            bounds=bounds,
            constraints=cons,
            options={'maxiter': 1000, 'ftol': 1e-14}
        )

        if result.success:
            return result.x
        else:
            return np.ones(n) / n