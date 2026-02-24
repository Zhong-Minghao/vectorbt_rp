"""
辅助工具函数
"""

import pandas as pd
import numpy as np
from typing import Union, Optional


def load_price_data(
    filepath: str,
    index_col: int = 0,
    parse_dates: bool = True
) -> pd.DataFrame:
    """
    加载价格数据

    Args:
        filepath: CSV 文件路径
        index_col: 索引列
        parse_dates: 是否解析日期

    Returns:
        价格数据 DataFrame
    """
    price_df = pd.read_csv(filepath, index_col=index_col)

    # 如果索引是字符串日期，转换为 datetime
    if parse_dates and not isinstance(price_df.index, pd.DatetimeIndex):
        price_df.index = pd.to_datetime(price_df.index)

    # 设置索引名称
    price_df.index.name = 'Date'

    # 设置列名称
    price_df.columns.name = 'symbol'

    return price_df


def get_month_end_rebalance(price_df: pd.DataFrame) -> pd.Series:
    """
    返回每月最后一个交易日的 True/False series

    Args:
        price_df: 价格数据 DataFrame

    Returns:
        布尔 Series，True 表示月末交易日
    """
    month_ends = price_df.groupby(
        [price_df.index.year, price_df.index.month]
    ).tail(1).index

    return pd.Series(price_df.index.isin(month_ends), index=price_df.index)


def get_rebalance_dates(
    price_df: pd.DataFrame,
    freq: str = 'ME'
) -> pd.DatetimeIndex:
    """
    获取指定频率的调仓日期

    Args:
        price_df: 价格数据 DataFrame
        freq: 频率 ('ME'=月末, 'MS'=月初, 'QE'=季末, 'W'=周等)

    Returns:
        调仓日期索引
    """
    return price_df.resample(freq).last().index


def clean_price_data(price_df: pd.DataFrame) -> pd.DataFrame:
    """
    清理价格数据

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


def calculate_returns(
    price_df: pd.DataFrame,
    method: str = 'pct_change'
) -> pd.DataFrame:
    """
    计算收益率

    Args:
        price_df: 价格数据
        method: 计算方法 ('pct_change' 或 'log')

    Returns:
        收益率 DataFrame
    """
    if method == 'pct_change':
        return price_df.pct_change(fill_method=None).dropna()
    elif method == 'log':
        return np.log(price_df / price_df.shift(1)).dropna()
    else:
        raise ValueError(f"Unknown method: {method}")


def annualize_metrics(
    daily_return: float,
    daily_vol: float,
    trading_days_per_year: int = 252
) -> tuple:
    """
    年化指标

    Args:
        daily_return: 日收益率
        daily_vol: 日波动率
        trading_days_per_year: 每年交易日数

    Returns:
        (年化收益率, 年化波动率)
    """
    annual_return = daily_return * trading_days_per_year
    annual_vol = daily_vol * np.sqrt(trading_days_per_year)

    return annual_return, annual_vol
