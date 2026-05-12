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
    df = df.replace([np.inf, -np.inf], np.nan).infer_objects(copy=False)    # infer_objects将数据类型转换为更合适的类型（如 float32）
    df = df.mask(df <= 0, np.nan)
    df = df.ffill()
    df = df.dropna(axis=1, how='all')
    df = df.dropna()

    return df


def align_columns(this_set: set, dfs: list[pd.DataFrame.columns]) -> list:
    """
    对齐set和dataframe.columns

    Args:
        this_set: 需要对齐的 set
        dfs: 需要对齐的 DataFrame 列表

    Returns:
        对齐后的 DataFrame 列表
    """
    # 检查是否有缺失/多余资产
    missing = [c for c in this_set.keys() if c not in dfs]
    extra = [c for c in dfs if c not in this_set]
    if missing or extra:
        raise ValueError(f"列名不匹配: missing={missing} extra={extra}")

    # 按 price_df 列顺序提取权重列表
    risk_weights_list = [this_set[col] for col in dfs]

    # 可选：保存为 numpy array
    # risk_weights_array = np.array(risk_weights_list)

    return risk_weights_list