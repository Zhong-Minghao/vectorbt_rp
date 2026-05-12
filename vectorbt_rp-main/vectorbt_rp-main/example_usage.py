"""
Portfolio Backtest Framework 使用示例
演示如何使用框架进行策略回测
"""

import pandas as pd
from portfolio_backtest import (
    BacktestEngine,
    RiskParityStrategy,
    MeanVarianceStrategy
)
from portfolio_backtest.visualization import BacktestVisualizer
from portfolio_backtest.utils import load_price_data


def example_risk_parity():
    """示例1：风险平价策略回测"""
    print("\n" + "="*60)
    print("示例1：风险平价策略回测")
    print("="*60)

    # 1. 加载数据
    price_df = load_price_data('./market_close.csv')
    print(f"加载数据: {price_df.shape}")

    # 2. 创建策略
    strategy = RiskParityStrategy(
        lookback=60,
        rebalance_freq='ME'
    )

    # 3. 创建回测引擎
    engine = BacktestEngine(
        init_cash=1_000_000,
        freq='1D',
        cash_sharing=True
    )

    # 4. 运行回测
    result = engine.run(strategy, price_df)

    # 5. 打印指标
    result.stats()

    # 6. 可视化
    visualizer = BacktestVisualizer(result)
    visualizer.print_metrics()
    visualizer.plot_summary()
    visualizer.plot_weights_heatmap()


def example_mean_variance():
    """示例2：均值方差策略回测"""
    print("\n" + "="*60)
    print("示例2：均值方差策略回测（最大化夏普比率）")
    print("="*60)

    # 加载数据
    price_df = load_price_data('./market_close.csv')

    # 创建策略
    strategy = MeanVarianceStrategy(
        lookback=60,
        rebalance_freq='ME'
    )

    # 运行回测
    engine = BacktestEngine(init_cash=1_000_000)
    result = engine.run(strategy, price_df)

    # 可视化
    visualizer = BacktestVisualizer(result)
    visualizer.print_metrics()
    visualizer.plot_summary()


def example_compare_strategies():
    """示例3：比较多个策略"""
    print("\n" + "="*60)
    print("示例3：策略对比")
    print("="*60)

    # 加载数据
    price_df = load_price_data('./market_close.csv')

    # 创建多个策略
    strategies = [
        RiskParityStrategy(lookback=60, rebalance_freq='ME'),
        MeanVarianceStrategy(lookback=60, rebalance_freq='ME'),
        MeanVarianceStrategy(lookback=120, rebalance_freq='QE'),  # 季度调仓
    ]

    # 比较策略
    engine = BacktestEngine(init_cash=1_000_000)
    comparison_df = engine.compare_strategies(
        strategies,
        price_df,
        names=['风险平价(60日)', '均值方差(60日)', '均值方差(120日季度)']
    )

    print("\n策略对比:")
    print(comparison_df)

    return comparison_df


def example_custom_strategy():
    """示例4：创建自定义策略"""
    print("\n" + "="*60)
    print("示例4：等权重策略（自定义策略示例）")
    print("="*60)

    from portfolio_backtest.strategies.base import BaseStrategy

    class EqualWeightStrategy(BaseStrategy):
        """等权重策略示例"""

        def __init__(self, rebalance_freq='ME'):
            super().__init__(name="Equal Weight", rebalance_freq=rebalance_freq)
            self.rebalance_freq = rebalance_freq

        def generate_weights(self, price_df, rebalance_mask=None):
            price_df = self.validate_data(price_df)

            if rebalance_mask is None:
                rebalance_dates = self.get_rebalance_dates(price_df, self.rebalance_freq)
                rebalance_mask = pd.Series(
                    price_df.index.isin(rebalance_dates),
                    index=price_df.index
                )

            n_assets = price_df.shape[1]
            equal_weight = 1.0 / n_assets

            # 只在调仓日生成权重
            rebalance_dates = price_df.index[rebalance_mask]

            weights_list = [np.full(n_assets, equal_weight) for _ in rebalance_dates]

            return pd.DataFrame(
                weights_list,
                index=rebalance_dates,
                columns=price_df.columns
            )

    # 使用自定义策略
    price_df = load_price_data('./market_close.csv')
    strategy = EqualWeightStrategy(rebalance_freq='ME')

    engine = BacktestEngine(init_cash=1_000_000)
    result = engine.run(strategy, price_df)

    visualizer = BacktestVisualizer(result)
    visualizer.print_metrics()

    return result


def example_visualization():
    """示例5：可视化功能展示"""
    print("\n" + "="*60)
    print("示例5：可视化功能展示")
    print("="*60)

    # 加载数据并运行回测
    price_df = load_price_data('./market_close.csv')
    strategy = RiskParityStrategy(lookback=60, rebalance_freq='ME')
    engine = BacktestEngine(init_cash=1_000_000)
    result = engine.run(strategy, price_df)

    # 创建可视化器
    viz = BacktestVisualizer(result)

    # 各种图表
    viz.plot_summary()
    viz.plot_performance_metrics()
    viz.plot_drawdown()
    viz.plot_weights_stacked(freq='QE')


def example_multiple_comparison():
    """示例6：多策略全面对比"""
    print("\n" + "="*60)
    print("示例6：多策略全面对比")
    print("="*60)

    price_df = load_price_data('./market_close.csv')

    # 运行多个策略
    engine = BacktestEngine(init_cash=1_000_000)

    strategies = [
        RiskParityStrategy(lookback=60, rebalance_freq='ME'),
        RiskParityStrategy(lookback=120, rebalance_freq='QE'),
        MeanVarianceStrategy(lookback=60, rebalance_freq='ME'),
    ]

    names = ['RP-60日-月度', 'RP-120日-季度', 'MV-60日-月度']

    results = []
    for strategy, name in zip(strategies, names):
        result = engine.run(strategy, price_df)
        results.append(result)
        print(f"\n{name} 回测完成")
        print(f"总收益: {result.metrics['total_return']*100:.2f}%")
        print(f"夏普比率: {result.metrics['sharpe_ratio']:.3f}")

    # 可视化对比
    BacktestVisualizer.compare_results(results, names=names)

    # 指标对比表
    comparison_table = BacktestVisualizer.compare_metrics_table(results, names)
    print("\n策略对比表:")
    print(comparison_table)


if __name__ == "__main__":
    # 运行示例

    # 示例1：风险平价策略
    example_risk_parity()

    # 示例2：均值方差策略
    # example_mean_variance()

    # 示例3：策略对比
    # example_compare_strategies()

    # 示例4：自定义策略
    # example_custom_strategy()

    # 示例5：可视化功能
    # example_visualization()

    # 示例6：多策略全面对比
    # example_multiple_comparison()
