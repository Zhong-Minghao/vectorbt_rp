"""
风险模型基类
"""

from abc import ABC, abstractmethod
from typing import Optional
import numpy as np
import pandas as pd


class BaseRiskModel(ABC):
    """
    风险模型基类

    所有风险模型都应继承此类并实现 estimate_risk 方法
    """

    def __init__(self, name: str, **params):
        """
        初始化风险模型

        Args:
            name: 模型名称
            **params: 模型参数
        """
        self.name = name
        self.params = params

    @abstractmethod
    def estimate_risk(self, returns: pd.DataFrame) -> np.ndarray:
        """
        估计风险模型

        Args:
            returns: 收益率 DataFrame

        Returns:
            协方差矩阵
        """
        pass

    def get_info(self) -> dict:
        """
        获取模型信息

        Returns:
            包含模型名称和参数的字典
        """
        return {
            "name": self.name,
            "params": self.params
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', params={self.params})"