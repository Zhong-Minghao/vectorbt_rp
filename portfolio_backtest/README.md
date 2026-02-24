# 投资组合回测框架

一个可扩展的投资组合回测框架，支持多种策略的快速回测和对比。

## 项目结构

```
portfolio_backtest/
├── __init__.py
├── strategies/              # 策略模块
│   ├── __init__.py
│   ├── base.py             # 策略基类
│   ├── risk_parity.py      # 风险平价策略
│   └── mean_variance.py    # 均值方差策略
├── engine/                  # 回测引擎
│   ├── __init__.py
│   └── backtest.py         # 通用回测引擎
├── visualization/           # 可视化模块
│   ├── __init__.py
│   └── plots.py            # 图表展示
└── utils/                   # 工具函数
    ├── __init__.py
    └── helpers.py          # 辅助函数
```

## 快速开始

### 基本用法

```python
from portfolio_backtest import (
    BacktestEngine,
    RiskParityStrategy,
    MeanVarianceStrategy
)
from portfolio_backtest.visualization import BacktestVisualizer
from portfolio_backtest.utils import load_price_data

# 1. 加载数据
price_df = load_price_data('./market_close.csv')

# 2. 创建策略
strategy = RiskParityStrategy(
    lookback=60,           # 60日回看窗口
    rebalance_freq='ME'    # 月末调仓
)

# 3. 创建回测引擎并运行
engine = BacktestEngine(init_cash=1_000_000)
result = engine.run(strategy, price_df)

# 4. 可视化结果
viz = BacktestVisualizer(result)
viz.print_metrics()
viz.plot_summary()
```

### 创建自定义策略

```python
from portfolio_backtest.strategies.base import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self, **params):
        super().__init__(name="My Strategy", **params)

    def generate_weights(self, price_df, rebalance_mask=None):
        # 实现你的权重生成逻辑
        # 返回 DataFrame: 索引为调仓日，列为资产
        pass
```

## 已实现的策略

### 1. RiskParityStrategy（风险平价策略）

目标：使得每个资产对组合的风险贡献相等

参数：
- `lookback`: 协方差矩阵回看窗口（默认60天）
- `rebalance_freq`: 调仓频率（默认'ME'月末）

### 2. MeanVarianceStrategy（均值方差策略）

基于 Markowitz 现代投资组合理论

参数：
- `lookback`: 均值和协方差回看窗口
- `rebalance_freq`: 调仓频率
- `target_return`: 目标收益率（可选，默认优化夏普比率）
- `weight_bounds`: 权重边界（默认(0, 1)）

## API 参考

### BacktestEngine

通用回测引擎，支持任何继承自 `BaseStrategy` 的策略。

```python
engine = BacktestEngine(
    init_cash=1_000_000,    # 初始资金
    freq='1D',              # 数据频率
    cash_sharing=True       # 共享资金池
)

# 运行单个策略
result = engine.run(strategy, price_df)

# 比较多个策略
comparison_df = engine.compare_strategies(
    strategies=[strategy1, strategy2],
    price_df=price_df,
    names=['策略1', '策略2']
)
```

### BacktestVisualizer

回测结果可视化器。

```python
viz = BacktestVisualizer(result)

# 打印性能指标
viz.print_metrics()

# 绘制图表
viz.plot_summary()              # 概览图
viz.plot_performance_metrics()  # 性能指标柱状图
viz.plot_weights_heatmap()      # 权重热力图
viz.plot_weights_stacked()      # 权重堆叠图
viz.plot_drawdown()             # 回撤图

# 对比多个策略
BacktestVisualizer.compare_results(results, names)
comparison_table = BacktestVisualizer.compare_metrics_table(results, names)
```

### BacktestResult

回测结果数据类。

```python
result.portfolio      # vectorbt Portfolio 对象
result.weights        # 权重 DataFrame
result.strategy       # 策略对象
result.metrics        # 性能指标字典

result.stats()        # 获取完整统计信息
```

## 调仓频率选项

- `'ME'`: 月末 (Month End)
- `'MS'`: 月初 (Month Start)
- `'QE'`: 季末 (Quarter End)
- `'QS'`: 季初 (Quarter Start)
- `'YE'`: 年末 (Year End)
- `'YS'`: 年初 (Year Start)
- `'W'`: 周末

## 依赖

- numpy
- pandas
- vectorbt
- scipy
- plotly

## 示例

完整示例请参考：
- `example_usage.py` - Python 脚本示例
- `portfolio_demo.ipynb` - Jupyter Notebook 示例
