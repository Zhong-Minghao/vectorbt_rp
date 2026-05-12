"""
策略基类
所有策略都应继承此类并实现 generate_weights 方法
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np


class BaseStrategy(ABC):
    """
    投资组合策略基类

    所有策略类都需要：
    1. 继承此类
    2. 实现 generate_weights 方法
    3. 定义策略名称
    """

    def __init__(self, name: str, **params):
        """
        初始化策略

        Args:
            name: 策略名称
            **params: 策略参数
        """
        self.name = name
        self.params = params
        self.weights_cache = None

    @abstractmethod
    def generate_weights(
        self,
        price_df: pd.DataFrame,
        rebalance_mask: pd.Series
    ) -> pd.DataFrame:
        """
        生成投资组合权重

        Args:
            price_df: 价格数据 DataFrame，索引为日期，列为资产
            rebalance_mask: 调仓日标记 Series，索引与 price_df 相同，True 表示调仓日

        Returns:
            权重 DataFrame，索引为调仓日，列为资产
        """
        pass

    def get_rebalance_dates(self, price_df: pd.DataFrame, freq: str = 'ME') -> pd.DatetimeIndex:
        """
        获取调仓日期

        Args:
            price_df: 价格数据
            freq: 调仓频率 ('ME'=月末, 'MS'=月初, 'QE'=季末, 'W'=周等)

        Returns:
            调仓日期索引（确保所有日期都在 price_df 的索引中）
        """
        # 方法：先将日期转换为Period，再转回Date，这样可以获得日历日期
        # 然后从 price_df 中找到该日历日期所在的周期内的最后一个实际交易日

        # 将 resample 频率别名转换为 Period 兼容的频率
        # 'ME' (month end) -> 'M' (month)
        # 'MS' (month start) -> 'M' (month)
        # 'QE' (quarter end) -> 'Q' (quarter)
        # 'QS' (quarter start) -> 'Q' (quarter)
        # 'W' (week) -> 'W' (week)
        freq_mapping = {
            'ME': 'M', 'MS': 'M', 'M': 'M',
            'QE': 'Q', 'QS': 'Q', 'Q': 'Q',
            'YE': 'Y', 'YS': 'Y', 'Y': 'Y', 'A': 'Y',
            'W': 'W', 'D': 'D'
        }
        period_freq = freq_mapping.get(freq, freq)

        # 获取所有唯一日期并转换为Period
        periods = price_df.index.to_period(period_freq)

        # 对每个周期，找到最后一个交易日
        unique_periods = periods.unique()
        rebalance_dates = []

        for period in unique_periods:
            # 获取该周期内的所有交易日
            mask = periods == period
            period_dates = price_df.index[mask]
            # 取最后一个交易日
            if len(period_dates) > 0:
                rebalance_dates.append(period_dates[-1])

        return pd.DatetimeIndex(rebalance_dates)

    def validate_data(self, price_df: pd.DataFrame) -> pd.DataFrame:
        """
        验证和清理价格数据

        Args:
            price_df: 原始价格数据

        Returns:
            清理后的价格数据
        """
        df = price_df.copy()

        # 处理无效值
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.mask(df <= 0, np.nan)
        df = df.ffill()
        df = df.dropna(axis=1, how='all')
        df = df.dropna()

        return df

    def get_info(self) -> Dict[str, Any]:
        """
        获取策略信息

        Returns:
            包含策略名称和参数的字典
        """
        return {
            "name": self.name,
            "params": self.params
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', params={self.params})"
