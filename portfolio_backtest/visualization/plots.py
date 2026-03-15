"""
可视化展示模块
用于展示回测结果
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
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
            height=400
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
            height=400
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

    def plot_assets_and_weights(
        self,
        price_df: pd.DataFrame,
        asset_name: Optional[str] = None,
        show: bool = True,
        freq: str = 'W',
        normalize_price: bool = True,
        weight_alpha: float = 0.3,
        return_fig: bool = False
    ) -> Optional[go.Figure]:
        """
        绘制单一资产的价格走势和权重变化的组合分析图

        该图展示：
        - 资产价格走势（折线图）
        - 叠加仓位变化（柱状图，带透明度）
        - 使用双y轴：左侧价格，右侧权重
        - 帮助分析模型何时对该资产进行加减仓

        Args:
            price_df: 价格数据 DataFrame
            asset_name: 要查看的资产名称（None=使用权重最大的资产）
            show: 是否显示图表
            freq: 权重重采样频率 ('D'=日, 'W'=周, 'M'=月)
            normalize_price: 是否归一化价格（初始价格=100）
            weight_alpha: 权重柱状图的透明度（0-1，越小越透明）
            return_fig: 是否返回 Figure 对象

        Returns:
            plotly Figure 对象（当 return_fig=True 时）
        """
        # 如果未指定资产，选择平均权重最大的资产
        if asset_name is None:
            avg_weights = self.weights.mean().sort_values(ascending=False)
            asset_name = avg_weights.index[0]

        # 验证资产是否存在
        if asset_name not in price_df.columns:
            raise ValueError(f"资产 '{asset_name}' 不在价格数据中。可用资产: {list(price_df.columns)}")

        if asset_name not in self.weights.columns:
            raise ValueError(f"资产 '{asset_name}' 不在权重数据中。可用资产: {list(self.weights.columns)}")

        # 提取该资产的价格和权重数据
        asset_price = price_df[asset_name]

        # 归一化价格数据（如果需要）
        if normalize_price:
            asset_price_normalized = (asset_price / asset_price.iloc[0]) * 100
            price_ylabel = "归一化价格 (初始=100)"
        else:
            asset_price_normalized = asset_price
            price_ylabel = "价格"

        # 按频率重采样权重数据
        asset_weights = self.weights[asset_name].resample(freq).first()

        # 创建图形（使用次要y轴）
        fig = go.Figure()

        # 添加价格走势（折线图）
        fig.add_trace(
            go.Scatter(
                x=asset_price_normalized.index,
                y=asset_price_normalized.values,
                name='价格',
                mode='lines',
                line=dict(color='#1f77b4', width=2),
                yaxis='y'
            )
        )

        # 计算柱状图的宽度（让柱子更紧凑）
        # 获取时间间隔，让柱子宽度占间隔的 90%
        if len(asset_weights) > 1:
            time_diff = (asset_weights.index[1] - asset_weights.index[0]).total_seconds()
            # 将时间差转换为天数（plotly 使用毫秒）
            bar_width = time_diff * 1000 * 0.9  # 90% 的间隔宽度
        else:
            bar_width = None

        # 添加权重变化（柱状图，带透明度，紧凑间隔）
        fig.add_trace(
            go.Bar(
                x=asset_weights.index,
                y=asset_weights.values,
                name='权重',
                width=bar_width,  # 设置柱子宽度，减少间隔
                marker=dict(
                    color='#ff7f0e',
                    opacity=weight_alpha,
                    line=dict(width=0)  # 移除边框
                ),
                yaxis='y2',
                hovertemplate='<b>%{x}</b><br>权重: %{y:.4f}<extra></extra>'
            )
        )

        # 更新布局
        fig.update_layout(
            title=f"{self.result.strategy.name} 策略 - {asset_name} 走势与仓位分析",
            height=500,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            # 双y轴配置（兼容新版 plotly）
            yaxis=dict(
                title=dict(
                    text=price_ylabel,
                    font=dict(color='#1f77b4')
                ),
                tickfont=dict(color='#1f77b4'),
                side='left'
            ),
            yaxis2=dict(
                title=dict(
                    text='权重',
                    font=dict(color='#ff7f0e')
                ),
                tickfont=dict(color='#ff7f0e'),
                overlaying='y',
                side='right',
                range=[0, asset_weights.max() * 1.2]  # 给权重留一些空间
            ),
            xaxis=dict(title='日期')
        )

        if show:
            fig.show()

        if return_fig:
            return fig
        return None

    def _calculate_effectiveness(
        self,
        price_df: pd.DataFrame,
        asset_name: str
    ) -> pd.DataFrame:
        """
        计算单次调仓的有效性（私有方法）

        单次调仓有效性 = (新权重 - 旧权重) × (期间收益率)

        Args:
            price_df: 价格数据 DataFrame
            asset_name: 资产名称

        Returns:
            包含每次调仓有效性的 DataFrame
        """
        # 获取该资产的权重数据
        asset_weights = self.weights[asset_name]

        # 只保留权重有数据的行（调仓日）
        asset_weights = asset_weights.dropna()

        # 获取价格数据
        asset_price = price_df[asset_name]

        # 计算每次调仓的有效性
        effectiveness_list = []

        # 遍历所有调仓日（除了最后一个，因为需要计算到下次调仓的收益）
        for i in range(len(asset_weights) - 1):
            # 当前调仓日
            current_date = asset_weights.index[i]
            # 下一次调仓日
            next_date = asset_weights.index[i + 1]

            # 调仓前权重（前一次调仓的权重，如果是第一次则为0）
            if i == 0:
                old_weight = 0.0
            else:
                old_weight = asset_weights.iloc[i - 1]

            # 调仓后权重（当前调仓的权重）
            new_weight = asset_weights.iloc[i]

            # 计算期间收益率（从当前调仓日到下一次调仓日）
            # 确保价格数据包含这两个日期
            if current_date in asset_price.index and next_date in asset_price.index:
                current_price = asset_price[current_date]
                next_price = asset_price[next_date]
                period_return = (next_price / current_price) - 1
            else:
                # 如果价格数据不完整，使用最接近的日期
                current_price = asset_price.asof(current_date)
                next_price = asset_price.asof(next_date)
                period_return = (next_price / current_price) - 1

            # 单次调仓有效性
            weight_change = new_weight - old_weight
            effectiveness = weight_change * period_return

            effectiveness_list.append({
                'date': current_date,
                'old_weight': old_weight,
                'new_weight': new_weight,
                'weight_change': weight_change,
                'period_return': period_return,
                'effectiveness': effectiveness
            })

        # 转换为 DataFrame
        effectiveness_df = pd.DataFrame(effectiveness_list)
        effectiveness_df.set_index('date', inplace=True)

        return effectiveness_df

    def plot_rebalancing_effectiveness(
        self,
        price_df: pd.DataFrame,
        asset_name: Optional[str] = None,
        show: bool = True,
        return_fig: bool = False
    ) -> Optional[go.Figure]:
        """
        分析和可视化单次调仓的有效性

        核心公式：
        单次调仓有效性 = (调仓后权重 - 调仓前权重) × (调仓后期间收益率)

        逻辑解释：
        - 正值（>0）：加仓且涨了，或减仓且跌了 → 正确决策
        - 负值（<0）：加仓但跌了，或减仓但涨了 → 错误决策

        可视化内容：
        - 上方：每次调仓的柱状图（绿色=正确，红色=错误）
        - 下方：累计乘积曲线（(1+有效性) 的累乘效果）

        Args:
            price_df: 价格数据 DataFrame
            asset_name: 要分析的资产名称（None=使用权重最大的资产）
            show: 是否显示图表
            return_fig: 是否返回 Figure 对象

        Returns:
            plotly Figure 对象（当 return_fig=True 时）
        """
        # 如果未指定资产，选择平均权重最大的资产
        if asset_name is None:
            avg_weights = self.weights.mean().sort_values(ascending=False)
            asset_name = avg_weights.index[0]

        # 验证资产是否存在
        if asset_name not in price_df.columns:
            raise ValueError(f"资产 '{asset_name}' 不在价格数据中")

        if asset_name not in self.weights.columns:
            raise ValueError(f"资产 '{asset_name}' 不在权重数据中")

        # 1. 计算单次调仓有效性
        effectiveness_df = self._calculate_effectiveness(price_df, asset_name)

        # 如果没有调仓数据
        if len(effectiveness_df) == 0:
            print(f"警告：资产 '{asset_name}' 没有调仓数据")
            return None

        # 2. 创建子图（2行1列）
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('单次调仓有效性', '累计乘积效果'),
            vertical_spacing=0.12,
            row_heights=[0.6, 0.4]
        )

        # 3. 添加柱状图（单次有效性）
        for idx, row in effectiveness_df.iterrows():
            color = '#2ca02c' if row['effectiveness'] > 0 else '#d62728'  # 绿色/红色

            fig.add_trace(
                go.Bar(
                    x=[idx],  # 使用索引（idx）而不是 row['date']
                    y=[row['effectiveness']],
                    marker_color=color,
                    opacity=0.7,
                    showlegend=False,
                    hovertemplate=f'<b>{idx.strftime("%Y-%m-%d")}</b><br>' +
                                   f'调仓前权重: {row["old_weight"]:.4f}<br>' +
                                   f'调仓后权重: {row["new_weight"]:.4f}<br>' +
                                   f'权重变化: {row["weight_change"]:+.4f}<br>' +
                                   f'期间收益: {row["period_return"]:+.4f}<br>' +
                                   f'有效性: {row["effectiveness"]:+.6f}<extra></extra>'
                ),
                row=1, col=1
            )

        # 4. 添加累计曲线
        cumulative = (1 + effectiveness_df['effectiveness']).cumprod()

        fig.add_trace(
            go.Scatter(
                x=cumulative.index,
                y=cumulative.values,
                mode='lines+markers',
                name='累计乘积',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=6),
                hovertemplate='<b>%{x}</b><br>累计乘积: %{y:.6f}<extra></extra>'
            ),
            row=2, col=1
        )

        # 5. 添加基准线
        fig.add_hline(
            y=0,
            line_dash="dash",
            line_width=1,
            line_color="gray",
            row=1, col=1
        )

        fig.add_hline(
            y=1,
            line_dash="dash",
            line_width=1,
            line_color="gray",
            annotation_text="基准线 (1.0)",
            row=2, col=1
        )

        # 6. 计算统计指标
        positive_count = (effectiveness_df['effectiveness'] > 0).sum()
        negative_count = (effectiveness_df['effectiveness'] < 0).sum()
        total_count = len(effectiveness_df)

        positive_ratio = positive_count / total_count if total_count > 0 else 0
        negative_ratio = negative_count / total_count if total_count > 0 else 0

        cumulative_product = cumulative.iloc[-1] if len(cumulative) > 0 else 1.0

        # 7. 更新布局和标题
        fig.update_layout(
            title=f"{self.result.strategy.name} 策略 - {asset_name} 调仓有效性分析<br>" +
                   f"<sup>正确决策: {positive_count}/{total_count} ({positive_ratio*100:.1f}%) | " +
                   f"错误决策: {negative_count}/{total_count} ({negative_ratio*100:.1f}%) | " +
                   f"累乘结果: {cumulative_product:.4f} ({(cumulative_product-1)*100:+.2f}%)</sup>",
            xaxis_title='调仓日期',
            yaxis_title='单次调仓有效性',
            height=800,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis2=dict(title='调仓次数'),
            yaxis2=dict(title='累计乘积')
        )

        if show:
            fig.show()

        if return_fig:
            return fig
        return None

    def plot_weight_changes_analysis(
        self,
        show: bool = True,
        threshold: float = 0.05,
        return_fig: bool = False
    ) -> Optional[go.Figure]:
        """
        分析权重变化并标注重要调仓点

        Args:
            show: 是否显示图表
            threshold: 权重变化阈值（超过此值将被标注）
            return_fig: 是否返回 Figure 对象

        Returns:
            plotly Figure 对象（当 return_fig=True 时）
        """
        # 计算权重变化
        weight_changes = self.weights.diff().abs()

        # 找出重要调仓点（权重变化超过阈值）
        significant_changes = weight_changes.max(axis=1) > threshold
        rebalance_dates = weight_changes.index[significant_changes]

        # 创建子图
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('各资产权重变化', '重要调仓点标注'),
            vertical_spacing=0.12,
            row_heights=[0.6, 0.4]
        )

        # 选择权重最大的前6个资产
        avg_weights = self.weights.mean().sort_values(ascending=False)
        top_assets = avg_weights.head(6).index.tolist()
        weights_filtered = self.weights[top_assets]

        colors = px.colors.qualitative.Set3[:len(top_assets)]

        # 添加权重变化曲线
        for i, asset in enumerate(top_assets):
            fig.add_trace(
                go.Scatter(
                    x=weights_filtered.index,
                    y=weights_filtered[asset],
                    name=asset,
                    mode='lines',
                    line=dict(color=colors[i], width=1.5),
                    stackgroup='one'  # 堆叠图
                ),
                row=1, col=1
            )

        # 添加调仓点标注
        for date in rebalance_dates:
            # 找出变化最大的资产
            changes_at_date = weight_changes.loc[date]
            max_change_asset = changes_at_date.idxmax()
            max_change_value = changes_at_date.max()

            # 在图中标注
            fig.add_trace(
                go.Scatter(
                    x=[date, date],
                    y=[0, 1],
                    mode='lines',
                    line=dict(color='red', width=1, dash='dash'),
                    showlegend=False,
                    hovertext=f"{date.strftime('%Y-%m-%d')}: {max_change_asset} 变化 {max_change_value:.1%}"
                ),
                row=2, col=1
            )

        # 添加调仓频率统计
        rebalance_counts = pd.Series(rebalance_dates.to_period('M').astype(str)).value_counts().sort_index()

        fig.add_trace(
            go.Bar(
                x=rebalance_counts.index,
                y=rebalance_counts.values,
                name='月度调仓次数',
                marker_color='lightblue',
                showlegend=False
            ),
            row=2, col=1
        )

        # 更新布局
        fig.update_layout(
            title=f"{self.result.strategy.name} 策略 - 权重变化与调仓分析",
            height=800,
            hovermode='x unified'
        )

        # 更新坐标轴
        fig.update_xaxes(title_text="日期", row=2, col=1)
        fig.update_yaxes(title_text="权重", row=1, col=1)
        fig.update_yaxes(title_text="调仓次数", row=2, col=1)

        if show:
            fig.show()

        if return_fig:
            return fig
        return None
