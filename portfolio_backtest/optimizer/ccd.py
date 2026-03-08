"""
CCD (Cyclical Coordinate Descent) 优化算法专门实现

用于风险平价优化的循环坐标下降算法
"""

import numpy as np
from typing import Optional
from .base import BaseOptimizer


class CCDOptimizer(BaseOptimizer):
    """
    CCD (Cyclical Coordinate Descent) 优化器

    专门用于求解风险平价问题的高效算法
    """

    def __init__(
        self,
        risk_budget: Optional[np.ndarray] = None,
        max_iter: int = 1000,
        tol: float = 1e-10,
        verbose: bool = False
    ):
        """
        初始化CCD优化器

        Args:
            risk_budget: 风险预算（默认等权重）
            max_iter: 最大迭代次数
            tol: 收敛容忍度
            verbose: 是否打印收敛信息
        """
        super().__init__(
            name="CCD Optimizer",
            risk_budget=risk_budget,
            max_iter=max_iter,
            tol=tol
        )
        self.risk_budget = risk_budget
        self.max_iter = max_iter
        self.tol = tol
        self.verbose = verbose

    def optimize(
        self,
        returns: Optional[np.ndarray] = None,
        cov_matrix: Optional[np.ndarray] = None,
        mean_returns: Optional[np.ndarray] = None,
        **kwargs
    ) -> np.ndarray:
        """
        使用CCD算法优化风险平价组合

        Args:
            returns: 收益率数据（如果未提供 cov_matrix 则需要）
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
            if isinstance(returns, np.ndarray):
                cov_matrix = np.cov(returns, rowvar=False)
            else:
                # 假设是 DataFrame
                import pandas as pd
                cov_matrix = returns.cov().values

        n = cov_matrix.shape[0]

        # 设置默认风险预算（等权重）
        if self.risk_budget is None:
            risk_budget = np.ones(n) / n
        else:
            risk_budget = self.risk_budget

        # 初始化权重
        x = np.ones(n)

        # CCD迭代
        for iteration in range(self.max_iter):
            x_old = x.copy()

            # 循环更新每个资产
            for i in range(n):
                a = cov_matrix[i, i]
                b = cov_matrix[i] @ x - a * x[i]
                c = risk_budget[i]
                x[i] = (-b + np.sqrt(b*b + 4*a*c)) / (2*a)

            # 检查收敛
            diff = np.linalg.norm(x - x_old)
            if diff < self.tol:
                if self.verbose:
                    print(f"CCD在第{iteration + 1}次迭代后收敛")
                break

        # 归一化权重
        weights = x / np.sum(x)

        if self.verbose and iteration == self.max_iter - 1:
            print(f"CCD达到最大迭代次数{self.max_iter}，最终差异：{diff:.2e}")

        return weights

    def get_convergence_info(self, cov_matrix: np.ndarray) -> dict:
        """
        获取收敛信息（用于调试和分析）

        Args:
            cov_matrix: 协方差矩阵

        Returns:
            包含收敛信息的字典
        """
        n = cov_matrix.shape[0]

        if self.risk_budget is None:
            risk_budget = np.ones(n) / n
        else:
            risk_budget = self.risk_budget

        x = np.ones(n)
        convergence_history = []

        for iteration in range(self.max_iter):
            x_old = x.copy()

            for i in range(n):
                a = cov_matrix[i, i]
                b = cov_matrix[i] @ x - a * x[i]
                c = risk_budget[i]
                x[i] = (-b + np.sqrt(b*b + 4*a*c)) / (2*a)

            diff = np.linalg.norm(x - x_old)
            convergence_history.append(diff)

            if diff < self.tol:
                break

        return {
            'iterations': iteration + 1,
            'final_diff': diff,
            'converged': diff < self.tol,
            'convergence_history': convergence_history
        }