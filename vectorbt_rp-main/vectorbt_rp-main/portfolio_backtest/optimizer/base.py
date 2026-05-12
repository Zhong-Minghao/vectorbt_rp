"""
优化器基类
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import numpy as np
import pandas as pd


class BaseOptimizer(ABC):
    """
    投资组合优化器基类

    所有优化器都应继承此类并实现 optimize 方法
    """

    def __init__(self, name: str, **params):
        """
        初始化优化器

        Args:
            name: 优化器名称
            **params: 优化器参数
        """
        self.name = name
        self.params = params

    @abstractmethod
    def optimize(
        self,
        returns: Optional[pd.DataFrame] = None,
        cov_matrix: Optional[np.ndarray] = None,
        mean_returns: Optional[np.ndarray] = None,
        **kwargs
    ) -> np.ndarray:
        """
        执行优化

        Args:
            returns: 收益率 DataFrame（可选）
            cov_matrix: 协方差矩阵（可选）
            mean_returns: 预期收益率（可选）
            **kwargs: 其他参数

        Returns:
            最优权重向量
        """
        pass

    def get_info(self) -> Dict[str, Any]:
        """
        获取优化器信息

        Returns:
            包含优化器名称和参数的字典
        """
        return {
            "name": self.name,
            "params": self.params
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', params={self.params})"