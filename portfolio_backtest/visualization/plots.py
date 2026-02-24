"""
可视化展示模块
用于展示回测结果
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional, List, Dict, Any, Union

from ..engine.backtest import BacktestResult


class BacktestVisualizer:
    """
    回测结果可视化器
    """

    def __init__(self, result: BacktestResult):
        """
        初始化可视化器

        Args:
            result: BacktestResult 对象
        """
        self.result = result
        self.portfolio = result.get_portfolio()
        self.weights = result.get_weights()
        self.metrics = result.get_metrics()

    def plot_summary(self, show: bool = True, return_fig: bool = False) -> Optional[go.Figure]:
        """
        绘制回测结果概览图

        包含：
        - 累计收益曲线
        - 资产价值
        - 现金持仓
        - 各资产价值

        Args:
            show: 是否显示图表
            return_fig: 是否返回 Figure 对象（设为 False 可避免 Jupyter 中重复显示）

        Returns:
            plotly Figure 对象（当 return_fig=True 时）
        """
        fig = self.portfolio.plot(subplots=['cum_returns'])

        fig.update_layout(
            title=f"{self.result.strategy.name} 策略回测结果",
            height=800
        )

        if show:
            fig.show()

        if return_fig:
            return fig
        return None

    def plot_performance_metrics(self, show: bool = True, return_fig: bool = False) -> Optional[go.Figure]:
        """
        绘制性能指标柱状图

        Args:
            show: 是否显示图表
            return_fig: 是否返回 Figure 对象

        Returns:
            plotly Figure 对象（当 return_fig=True 时）
        """
        # 选择关键指标
        key_metrics = {
            "年化收益率": self.metrics.get("annualized_return", 0) * 100,
            "年化波动率": self.metrics.get("annualized_volatility", 0) * 100,
            "夏普比率": self.metrics.get("sharpe_ratio", 0),
            "最大回撤": self.metrics.get("max_drawdown", 0) * 100,
            "Calmar比率": self.metrics.get("calmar_ratio", 0),
            "索提诺比率": self.metrics.get("sortino_ratio", 0),
        }

        fig = go.Figure(data=[
            go.Bar(
                x=list(key_metrics.keys()),
                y=list(key_metrics.values()),
                marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
            )
        ])

        fig.update_layout(
            title="策略性能指标",
            xaxis_title="指标",
            yaxis_title="数值",
            height=500
        )

        if show:
            fig.show()

        if return_fig:
            return fig
        return None

    def plot_weights_heatmap(self, show: bool = True, freq: str = 'ME', return_fig: bool = False) -> Optional[go.Figure]:
        """
        绘制权重变化热力图

        Args:
            show: 是否显示图表
            freq: 重采样频率 ('ME'=月末, 'QE'=季末等)
            return_fig: 是否返回 Figure 对象

        Returns:
            plotly Figure 对象（当 return_fig=True 时）
        """
        # 按频率重采样
        weights_resampled = self.weights.resample(freq).first()

        fig = go.Figure(data=go.Heatmap(
            z=weights_resampled.values.T,
            x=weights_resampled.index.strftime('%Y-%m'),
            y=weights_resampled.columns,
            colorscale='Viridis',
            colorbar=dict(title="权重")
        ))

        fig.update_layout(
            title="权重配置变化",
            xaxis_title="日期",
            yaxis_title="资产",
            height=600
        )

        if show:
            fig.show()

        if return_fig:
            return fig
        return None

    def plot_weights_stacked(self, show: bool = True, freq: str = 'ME', return_fig: bool = False) -> Optional[go.Figure]:
        """
        绘制权重堆叠面积图

        Args:
            show: 是否显示图表
            freq: 重采样频率
            return_fig: 是否返回 Figure 对象

        Returns:
            plotly Figure 对象（当 return_fig=True 时）
        """
        weights_resampled = self.weights.resample(freq).first()

        fig = go.Figure()

        for col in weights_resampled.columns:
            fig.add_trace(go.Scatter(
                x=weights_resampled.index,
                y=weights_resampled[col],
                name=col,
                stackgroup='one',
                mode='lines'
            ))

        fig.update_layout(
            title="各资产权重配置变化",
            xaxis_title="日期",
            yaxis_title="权重",
            height=500,
            hovermode='x unified'
        )

        if show:
            fig.show()

        if return_fig:
            return fig
        return None

    def plot_drawdown(self, show: bool = True, return_fig: bool = False) -> Optional[go.Figure]:
        """
        绘制回撤图

        Args:
            show: 是否显示图表
            return_fig: 是否返回 Figure 对象

        Returns:
            plotly Figure 对象（当 return_fig=True 时）
        """
        # 获取累计收益
        # 尝试多种方式获取累计收益，兼容不同版本的 vectorbt
        try:
            if hasattr(self.portfolio, 'get_cum_returns'):
                cum_returns = self.portfolio.get_cum_returns()
            elif hasattr(self.portfolio, 'cum_returns'):
                cum_returns = self.portfolio.cum_returns
            else:
                # 手动计算累计收益
                returns = self.portfolio.returns()
                cum_returns = (1 + returns).cumprod() - 1
        except Exception:
            # 作为后备方案，使用净值来计算
            cum_returns = self.portfolio.value() / self.portfolio.init_cash() - 1

        # 计算回撤
        running_max = cum_returns.cummax()
        drawdown = (cum_returns - running_max) / (1 + running_max)

        fig = go.Figure()

        # 添加累计收益曲线
        fig.add_trace(go.Scatter(
            x=cum_returns.index,
            y=cum_returns.values * 100,
            name='累计收益',
            line=dict(color='#2ca02c')
        ))

        # 添加回撤填充
        fig.add_trace(go.Scatter(
            x=drawdown.index,
            y=drawdown.values * 100,
            name='回撤',
            fill='tozeroy',
            line=dict(color='#d62728')
        ))

        fig.update_layout(
            title="累计收益与回撤",
            xaxis_title="日期",
            yaxis_title="收益率 (%)",
            height=500,
            hovermode='x unified'
        )

        if show:
            fig.show()

        if return_fig:
            return fig
        return None

    def print_metrics(self):
        """打印性能指标"""
        print(f"\n{'='*40}")
        print(f"{self.result.strategy.name} 策略表现")
        print(f"{'='*40}")

        print(f"总收益率: {self.metrics.get('total_return', 0) * 100:.2f}%")
        print(f"年化收益率: {self.metrics.get('annualized_return', 0) * 100:.2f}%")
        print(f"年化波动率: {self.metrics.get('annualized_volatility', 0) * 100:.2f}%")
        print(f"夏普比率: {self.metrics.get('sharpe_ratio', 0):.3f}")
        print(f"索提诺比率: {self.metrics.get('sortino_ratio', 0):.3f}")
        print(f"Calmar比率: {self.metrics.get('calmar_ratio', 0):.3f}")
        print(f"Omega比率: {self.metrics.get('omega_ratio', 0):.3f}")
        print(f"最大回撤: {self.metrics.get('max_drawdown', 0) * 100:.2f}%")

        if self.metrics.get('win_rate') is not None:
            print(f"胜率: {self.metrics.get('win_rate', 0):.2f}%")

        print(f"{'='*40}\n")

    @staticmethod
    def compare_results(
        results: List[BacktestResult],
        names: Optional[List[str]] = None,
        show: bool = True,
        return_fig: bool = False
    ) -> Optional[go.Figure]:
        """
        比较多个回测结果

        Args:
            results: BacktestResult 对象列表
            names: 策略名称列表
            show: 是否显示图表
            return_fig: 是否返回 Figure 对象

        Returns:
            plotly Figure 对象（当 return_fig=True 时）
        """
        if names is None:
            names = [r.strategy.name for r in results]

        fig = go.Figure()

        for result, name in zip(results, names):
            portfolio = result.get_portfolio()
            # 尝试多种方式获取累计收益，兼容不同版本的 vectorbt
            try:
                if hasattr(portfolio, 'get_cum_returns'):
                    cum_returns = portfolio.get_cum_returns()
                elif hasattr(portfolio, 'cum_returns'):
                    cum_returns = portfolio.cum_returns
                else:
                    # 手动计算累计收益
                    returns = portfolio.returns()
                    cum_returns = (1 + returns).cumprod() - 1
            except Exception:
                # 作为后备方案，使用净值来计算
                cum_returns = portfolio.value() / portfolio.init_cash() - 1

            fig.add_trace(go.Scatter(
                x=cum_returns.index,
                y=cum_returns.values * 100,
                name=name,
                mode='lines'
            ))

        fig.update_layout(
            title="策略累计收益对比",
            xaxis_title="日期",
            yaxis_title="累计收益 (%)",
            height=500,
            hovermode='x unified'
        )

        if show:
            fig.show()

        if return_fig:
            return fig
        return None

    @staticmethod
    def compare_metrics_table(
        results: List[BacktestResult],
        names: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        生成策略对比指标表

        Args:
            results: BacktestResult 对象列表
            names: 策略名称列表

        Returns:
            对比指标 DataFrame
        """
        if names is None:
            names = [r.strategy.name for r in results]

        comparison_data = {}

        for result, name in zip(results, names):
            metrics = result.get_metrics()
            comparison_data[name] = {
                "总收益率 (%)": metrics.get("total_return", 0) * 100,
                "年化收益率 (%)": metrics.get("annualized_return", 0) * 100,
                "年化波动率 (%)": metrics.get("annualized_volatility", 0) * 100,
                "夏普比率": metrics.get("sharpe_ratio", 0),
                "索提诺比率": metrics.get("sortino_ratio", 0),
                "Calmar比率": metrics.get("calmar_ratio", 0),
                "最大回撤 (%)": metrics.get("max_drawdown", 0) * 100,
            }

        return pd.DataFrame(comparison_data).T
