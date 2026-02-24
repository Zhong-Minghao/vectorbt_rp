"""
通用回测引擎
支持任何继承自 BaseStrategy 的策略
"""

import numpy as np
import pandas as pd
import vectorbt as vbt
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass, field

from ..strategies.base import BaseStrategy


@dataclass
class BacktestResult:
    """
    回测结果数据类
    """
    portfolio: vbt.Portfolio
    weights: pd.DataFrame
    strategy: BaseStrategy
    metrics: Dict[str, Any] = field(default_factory=dict)

    def get_portfolio(self) -> vbt.Portfolio:
        """获取 vectorbt Portfolio 对象"""
        return self.portfolio

    def get_weights(self) -> pd.DataFrame:
        """获取权重 DataFrame"""
        return self.weights

    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return self.metrics

    def stats(self) -> pd.Series:
        """获取完整统计信息"""
        return self.portfolio.stats()

    def __repr__(self) -> str:
        return f"BacktestResult(strategy={self.strategy.name}, total_return={self.metrics.get('total_return', 'N/A')})"


class BacktestEngine:
    """
    通用回测引擎

    支持任何继承自 BaseStrategy 的策略进行回测
    """

    def __init__(
        self,
        init_cash: float = 1_000_000,
        freq: str = '1D',
        cash_sharing: bool = True
    ):
        """
        初始化回测引擎

        Args:
            init_cash: 初始资金
            freq: 数据频率 ('1D'=日, '1h'=小时等)
            cash_sharing: 是否共享资金池
        """
        self.init_cash = init_cash
        self.freq = freq
        self.cash_sharing = cash_sharing

    def _clean_price_data(self, price_df: pd.DataFrame) -> pd.DataFrame:
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

    def _expand_weights_to_daily(
        self,
        weights_df: pd.DataFrame,
        price_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        将调仓日权重扩展到每日

        Args:
            weights_df: 调仓日权重 DataFrame
            price_df: 价格数据（用于获取完整日期索引）

        Returns:
            扩展后的每日权重 DataFrame
        """
        # 重新索引到完整的日期范围
        target = weights_df.reindex(price_df.index)

        # 非调仓日保持前一个权重（ffill）
        target = target.ffill()

        return target

    def run(
        self,
        strategy: BaseStrategy,
        price_df: pd.DataFrame,
        rebalance_mask: Optional[pd.Series] = None
    ) -> BacktestResult:
        """
        运行回测

        Args:
            strategy: 策略对象
            price_df: 价格数据 DataFrame，索引为日期，列为资产
            rebalance_mask: 调仓日标记（可选，如不提供则由策略生成）

        Returns:
            BacktestResult 对象
        """
        # 清理数据
        price_df = self._clean_price_data(price_df)

        # 生成权重
        weights_df = strategy.generate_weights(price_df, rebalance_mask)

        if weights_df.empty:
            raise ValueError("策略未生成任何权重，请检查数据或策略参数")

        # 扩展权重到每日
        daily_weights = self._expand_weights_to_daily(weights_df, price_df)

        # 对齐索引
        common_index = price_df.index.intersection(daily_weights.index)
        price_df_aligned = price_df.loc[common_index]
        daily_weights_aligned = daily_weights.loc[common_index]

        # 运行回测
        pf = vbt.Portfolio.from_orders(
            close=price_df_aligned,
            size=daily_weights_aligned,
            size_type="targetpercent",
            freq=self.freq,
            init_cash=self.init_cash,
            cash_sharing=self.cash_sharing
        )

        # 计算性能指标
        metrics = self._calculate_metrics(pf)

        return BacktestResult(
            portfolio=pf,
            weights=weights_df,
            strategy=strategy,
            metrics=metrics
        )

    def _calculate_metrics(self, portfolio: vbt.Portfolio) -> Dict[str, Any]:
        """
        计算性能指标

        Args:
            portfolio: vectorbt Portfolio 对象

        Returns:
            包含各项指标的字典
        """
        return {
            "total_return": portfolio.total_return(),
            "annualized_return": portfolio.annualized_return(),
            "annualized_volatility": portfolio.annualized_volatility(),
            "sharpe_ratio": portfolio.sharpe_ratio(),
            "sortino_ratio": portfolio.sortino_ratio(),
            "calmar_ratio": portfolio.calmar_ratio(),
            "max_drawdown": portfolio.max_drawdown(),
            "omega_ratio": portfolio.omega_ratio(),
            "best_trade": portfolio.stats()['best_trade'] if 'best_trade' in portfolio.stats() else None,
            "worst_trade": portfolio.stats()['worst_trade'] if 'worst_trade' in portfolio.stats() else None,
            "win_rate": portfolio.stats()['win_rate'] if 'win_rate' in portfolio.stats() else None,
        }

    def compare_strategies(
        self,
        strategies: list[BaseStrategy],
        price_df: pd.DataFrame,
        names: Optional[list[str]] = None
    ) -> pd.DataFrame:
        """
        比较多个策略的表现

        Args:
            strategies: 策略列表
            price_df: 价格数据
            names: 策略名称列表（可选）

        Returns:
            比较结果 DataFrame
        """
        if names is None:
            names = [s.name for s in strategies]

        results = {}

        for strategy, name in zip(strategies, names):
            try:
                result = self.run(strategy, price_df)
                metrics = result.get_metrics()
                results[name] = metrics
            except Exception as e:
                print(f"策略 {name} 回测失败: {e}")
                results[name] = None

        # 转换为 DataFrame
        comparison_df = pd.DataFrame(results).T

        return comparison_df

    def backtest_with_benchmark(
        self,
        strategy: BaseStrategy,
        price_df: pd.DataFrame,
        benchmark_col: str
    ) -> Dict[str, BacktestResult]:
        """
        策略与基准对比回测

        Args:
            strategy: 策略对象
            price_df: 价格数据
            benchmark_col: 基准列名

        Returns:
            包含策略和基准回测结果的字典
        """
        # 策略回测
        strategy_result = self.run(strategy, price_df)

        # 基准回测（等权重买入持有）
        benchmark_weights = pd.DataFrame(
            1.0,
            index=price_df.index,
            columns=[benchmark_col]
        )

        benchmark_price = price_df[[benchmark_col]].copy()

        pf_bench = vbt.Portfolio.from_orders(
            close=benchmark_price,
            size=benchmark_weights,
            size_type="targetpercent",
            freq=self.freq,
            init_cash=self.init_cash,
            cash_sharing=self.cash_sharing
        )

        benchmark_result = BacktestResult(
            portfolio=pf_bench,
            weights=benchmark_weights,
            strategy=strategy,  # 使用相同的策略信息
            metrics=self._calculate_metrics(pf_bench)
        )

        return {
            "strategy": strategy_result,
            "benchmark": benchmark_result
        }
