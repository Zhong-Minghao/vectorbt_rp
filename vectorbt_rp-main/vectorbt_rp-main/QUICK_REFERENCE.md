# 快速参考表

## 🎯 根据需求快速找到功能

### 我想...

| 需求 | 使用方法 | 代码示例 |
|------|----------|----------|
| 运行基本风险平价回测 | `RiskParityStrategy` | `strategy = RiskParityStrategy(lookback=60)` |
| 使用更快的优化算法 | 设置 `method='CDD'` | `RiskParityStrategy(method='CDD')` |
| 使用更稳定的协方差估计 | 设置 `risk_model='ledoit_wolf'` | `RiskParityStrategy(risk_model='ledoit_wolf')` |
| **自定义风险预算** 🆕 | 设置 `risk_budget` | `RiskParityStrategy(risk_budget=np.array([0.6, 0.4]))` |
| **分析资产价格与仓位** 🆕 | `plot_assets_and_weights()` | `viz.plot_assets_and_weights(price_df, asset_name='黄金')` |
| **对比调仓 vs 买入持有** 🆕 | `compare_dynamic_vs_buyhold()` | `viz.compare_dynamic_vs_buyhold(price_df, asset_name='股票')` |
| **分析调仓有效性** 🆕🔥 | `plot_rebalancing_effectiveness()` | `viz.plot_rebalancing_effectiveness(price_df, asset_name='股票')` |
| 直接使用优化器 | `RiskParityOptimizer` | `optimizer = RiskParityOptimizer(method='CDD')` |
| 直接估计协方差矩阵 | `CovarianceEstimator` | `estimator = CovarianceEstimator(method='ledoit_wolf')` |
| 运行均值方差优化 | `MeanVarianceStrategy` | `strategy = MeanVarianceStrategy(lookback=60)` |
| 最大化夏普比率 | `MeanVarianceOptimizer` | `optimizer = MeanVarianceOptimizer(objective='max_sharpe')` |
| 对比多个策略 | `engine.compare_strategies()` | `engine.compare_strategies(strategies, names)` |

## 📦 模块速查表

### Risk 模块 (`portfolio_backtest.risk`)

| 类 | 功能 | 主要参数 |
|---|------|----------|
| `CovarianceEstimator` | 协方差矩阵估计 | `method`: 'sample', 'ledoit_wolf', 'oracle_approximating' |
| `ShrinkageEstimator` | 协方差收缩估计 | `shrinkage_type`: 'constant_correlation', 'single_factor', 'identity' |
| `BaseRiskModel` | 风险模型基类 | 用于自定义风险模型 |

### Optimizer 模块 (`portfolio_backtest.optimizer`)

| 类 | 功能 | 主要参数 |
|---|------|----------|
| `RiskParityOptimizer` | 风险平价优化 | `method`: 'SLSQP', 'CDD' |
| `MeanVarianceOptimizer` | 均值方差优化 | `objective`: 'max_sharpe', 'min_variance', 'target_return' |
| `CCDOptimizer` | CCD 算法专门实现 | `max_iter`, `tol` |
| `BaseOptimizer` | 优化器基类 | 用于自定义优化器 |

### Strategy 模块 (`portfolio_backtest.strategies`)

| 类 | 功能 | 主要参数 |
|---|------|----------|
| `RiskParityStrategy` | 风险平价策略 | `lookback`, `method`, `risk_model` |
| `MeanVarianceStrategy` | 均值方差策略 | `lookback`, `target_return`, `risk_aversion` |
| `BaseStrategy` | 策略基类 | 用于自定义策略 |

### Engine 模块 (`portfolio_backtest.engine`)

| 类 | 功能 | 主要参数 |
|---|------|----------|
| `BacktestEngine` | 回测引擎 | `init_cash`, `freq`, `cash_sharing` |
| `BacktestResult` | 回测结果 | 包含 `portfolio`, `weights`, `metrics` |

## 🔧 参数速查表

### RiskParityStrategy 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `lookback` | int | 60 | 回看窗口（天数） |
| `rebalance_freq` | str | 'ME' | 调仓频率 ('ME'=月末, 'QE'=季末等) |
| `method` | str | 'SLSQP' | 优化方法 ('SLSQP' 或 'CDD') |
| `risk_model` | str | 'sample' | 风险模型 ('sample', 'ledoit_wolf', 'oracle_approximating') |
| `risk_budget` | array | None | 🆕 自定义风险预算（None=等权重，否则指定每个资产的风险贡献目标） |
| `compare_methods` | bool | False | 是否对比两种优化方法 |

### CovarianceEstimator 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `method` | str | 'sample' | 估计方法 |
| `annualize` | bool | False | 是否年化 |
| `trading_days` | int | 252 | 年化交易日数 |

### RiskParityOptimizer 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `method` | str | 'SLSQP' | 优化方法 |
| `risk_budget` | array | None | 风险预算（默认等权重） |
| `weight_bounds` | tuple | (0, 1) | 权重边界 |
| `max_iter` | int | 1000 | 最大迭代次数（CDD） |
| `tol` | float | 1e-10 | 收敛容忍度（CDD） |

### MeanVarianceOptimizer 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `objective` | str | 'max_sharpe' | 优化目标 |
| `target_return` | float | None | 目标收益率 |
| `risk_free_rate` | float | 0.0 | 无风险利率 |
| `risk_aversion` | float | 1.0 | 风险厌恶系数 |
| `weight_bounds` | tuple | (0, 1) | 权重边界 |

## 📊 性能指标速查表

### BacktestResult.metrics 包含的指标

| 指标 | 说明 | 计算方式 |
|------|------|----------|
| `total_return` | 总收益率 | (最终价值 - 初始价值) / 初始价值 |
| `annualized_return` | 年化收益率 | 总收益率年化 |
| `annualized_volatility` | 年化波动率 | 收益率标准差年化 |
| `sharpe_ratio` | 夏普比率 | (年化收益 - 无风险利率) / 年化波动率 |
| `sortino_ratio` | 索提诺比率 | 下行风险调整收益 |
| `calmar_ratio` | 卡玛比率 | 年化收益 / 最大回撤 |
| `max_drawdown` | 最大回撤 | 最大回撤幅度 |
| `omega_ratio` | Omega比率 | 上涨/下跌风险比率 |
| `best_trade` | 最佳交易 | 最大单次收益 |
| `worst_trade` | 最差交易 | 最大单次亏损 |
| `win_rate` | 胜率 | 盈利交易占比 |

## 🚀 常用代码片段

### 基本回测流程

```python
from portfolio_backtest import BacktestEngine, RiskParityStrategy
from portfolio_backtest.utils import load_price_data

# 1. 加载数据
price_df = load_price_data('data.csv')

# 2. 创建策略和引擎
strategy = RiskParityStrategy(lookback=60)
engine = BacktestEngine(init_cash=1_000_000)

# 3. 运行回测
result = engine.run(strategy, price_df)

# 4. 查看结果
print(result.metrics)
```

### 批量测试不同参数

```python
import pandas as pd

results = {}
for lookback in [20, 40, 60, 120]:
    strategy = RiskParityStrategy(lookback=lookback)
    result = engine.run(strategy, price_df)
    results[lookback] = result.metrics['annualized_return']

print(pd.Series(results))
```

### 策略对比

```python
strategies = [
    RiskParityStrategy(lookback=60, method='SLSQP'),
    RiskParityStrategy(lookback=60, method='CDD'),
    MeanVarianceStrategy(lookback=60)
]

comparison = engine.compare_strategies(
    strategies=strategies,
    names=['RP-SLSQP', 'RP-CDD', 'Mean-Var']
)
print(comparison)
```

### 提取权重数据

```python
# 获取调仓日权重
rebalance_weights = result.weights

# 扩展到每日（引擎内部已处理）
# 查看权重分布
result.weights.describe()

# 查看最后一次调仓权重
final_weights = result.weights.iloc[-1]
print(final_weights)
```

### 🆕 自定义风险预算

```python
import numpy as np
from portfolio_backtest import RiskParityStrategy

# 场景1: 保守型投资者 - 债券承担更多风险
conservative_budget = np.array([0.3, 0.5, 0.2])  # 股票30%, 债券50%, 商品20%
strategy = RiskParityStrategy(
    lookback=60,
    risk_budget=conservative_budget
)

# 场景2: 激进型投资者 - 股票承担更多风险
aggressive_budget = np.array([0.6, 0.2, 0.2])  # 股票60%, 债券20%, 商品20%
strategy = RiskParityStrategy(
    lookback=60,
    risk_budget=aggressive_budget
)

# 场景3: 行业轮动 - 超配科技和消费
sector_budget = np.array([0.15, 0.30, 0.25, 0.20, 0.10])  # 金融、科技、消费、医疗、能源
strategy = RiskParityStrategy(
    lookback=60,
    risk_budget=sector_budget
)

# 验证风险贡献
returns = price_df.pct_change().dropna()
window_ret = returns.tail(strategy.lookback)
cov_matrix = strategy.cov_estimator.estimate_risk(window_ret)
weights = strategy.optimizer.optimize(cov_matrix=cov_matrix)
risk_contrib = strategy.cov_estimator.calculate_risk_contribution(weights, cov_matrix)

print("实际风险贡献:", risk_contrib)
print("目标风险预算:", strategy.risk_budget)
```

### 🆕 资产价格与仓位分析

```python
from portfolio_backtest.visualization import BacktestVisualizer

viz = BacktestVisualizer(result)

# 分析权重最大的资产（自动选择）
viz.plot_assets_and_weights(
    price_df,
    freq='W',                # 按周显示仓位
    normalize_price=True,    # 归一化价格
    weight_alpha=0.3         # 权重柱状图透明度 (0-1)
)

# 分析指定资产
viz.plot_assets_and_weights(
    price_df,
    asset_name='黄金',       # 指定资产名称
    freq='W',
    normalize_price=True,
    weight_alpha=0.4
)

# 使用原始价格（不归一化）
viz.plot_assets_and_weights(
    price_df,
    asset_name='股票',
    freq='D',                # 日频，看更详细的仓位变化
    normalize_price=False,   # 使用原始价格
    weight_alpha=0.2         # 更低的透明度
)
```

### 🆕 对比动态调仓 vs 买入持有

```python
from portfolio_backtest.visualization import BacktestVisualizer

viz = BacktestVisualizer(result)

# 对比调仓效果
viz.compare_dynamic_vs_buyhold(
    price_df,
    asset_name='股票',           # 指定资产
    initial_investment=10000     # 初始投资金额
)

# 自动选择权重最大的资产对比
viz.compare_dynamic_vs_buyhold(
    price_df,
    initial_investment=50000
)
```

**图表解读：**
- 🔵 蓝色实线：动态调仓策略的资产价值变化
- 🟠 橙色虚线：买入持有策略的资产价值变化
- 📍 灰色虚线：重要调仓时点
- 📊 标题显示：动态调仓收益、买入持有收益、超额收益

**如何评估调仓合理性：**
1. ✅ 超额收益 > 0：调仓策略跑赢了买入持有
2. ⚠️ 超额收益 < 0：调仓策略跑输了，可能需要优化
3. 观察调仓点是否在趋势转折点附近
4. 对比不同资产的调仓效果

### 🔥 调仓有效性分析（精细评估）

```python
from portfolio_backtest.visualization import BacktestVisualizer

viz = BacktestVisualizer(result)

# 分析每次调仓决策的质量
viz.plot_rebalancing_effectiveness(
    price_df,
    asset_name='股票'           # 指定资产（None=自动选择）
)
```

**核心公式：**
```
单次调仓有效性 = (新权重 - 旧权重) × (期间收益率)
```

**图表解读：**
- 🟢 **绿色柱子**：正确决策（加仓涨了 / 减仓跌了）
- 🔴 **红色柱子**：错误决策（加仓跌了 / 减仓涨了）
- 🔵 **蓝色曲线**：累计乘积效果 `(1+有效性)` 的累乘
- 📊 **标题统计**：正确率、累乘结果、调仓次数

**评估标准：**
- ✅ 正确率 ≥ 70%：调仓质量优秀
- ✅ 正确率 60-70%：调仓质量良好
- ⚠️ 正确率 50-60%：调仓质量一般
- ❌ 正确率 < 50%：调仓质量较差，需要优化

**累乘结果含义：**
- > 1：整体提升了投资效果
- < 1：整体损害了投资效果

**公式原理示例：**
```python
# 场景1: 加仓且涨了 → 正确
旧权重 = 10%, 新权重 = 15%, 收益率 = 5%
有效性 = (15% - 10%) × 5% = +0.0025 ✅

# 场景2: 减仓且跌了 → 正确
旧权重 = 15%, 新权重 = 10%, 收益率 = -3%
有效性 = (10% - 15%) × (-3%) = +0.0015 ✅

# 场景3: 加仓但跌了 → 错误
旧权重 = 10%, 新权重 = 15%, 收益率 = -2%
有效性 = (15% - 10%) × (-2%) = -0.0010 ❌
```

## 🔍 调试技巧

### 检查协方差矩阵

```python
from portfolio_backtest.risk import CovarianceEstimator
import numpy as np

estimator = CovarianceEstimator(method='ledoit_wolf')
cov_matrix = estimator.estimate_risk(returns)

# 检查性质
print(f"形状: {cov_matrix.shape}")
print(f"条件数: {np.linalg.cond(cov_matrix):.2f}")
print(f"是否正定: {np.all(np.linalg.eigvals(cov_matrix) > 0)}")
```

### 检查优化结果

```python
from portfolio_backtest.optimizer import RiskParityOptimizer

optimizer = RiskParityOptimizer(method='SLSQP')
weights = optimizer.optimize(cov_matrix=cov_matrix)

# 检查约束
print(f"权重和: {np.sum(weights):.6f}")  # 应该接近 1
print(f"权重范围: [{weights.min():.4f}, {weights.max():.4f}]")
print(f"负权重数: {np.sum(weights < 0)}")
```

### 验证风险平价

```python
# 计算风险贡献
portfolio_var = weights.T @ cov_matrix @ weights
marginal_contrib = cov_matrix @ weights
risk_contrib = weights * marginal_contrib
percentage_rc = risk_contrib / portfolio_var

print("风险贡献百分比:")
print(percentage_rc)
print(f"标准差: {np.std(percentage_rc):.6f}")  # 应该接近 0
```

## 💡 最佳实践

### 1. 选择合适的回看窗口

| 调仓频率 | 推荐回看窗口 | 说明 |
|----------|--------------|------|
| 日 | 20-60 | 捕捉短期风险特征 |
| 周 | 40-120 | 平衡短期和中期 |
| 月 | 60-252 | 使用更多历史数据 |
| 季 | 120-252 | 长期风险估计 |

### 2. 协方差估计方法选择

| 情况 | 推荐方法 | 理由 |
|------|----------|------|
| 资产数 < 10 | 'sample' | 数据充足，样本估计准确 |
| 资产数 10-50 | 'ledoit_wolf' | 需要收缩，提高稳定性 |
| 资产数 > 50 | 'ledoit_wolf' | 必须收缩，避免过拟合 |
| 数据质量差 | 'oracle_approximating' | 更鲁棒的估计 |

### 3. 优化算法选择

| 情况 | 推荐算法 | 理由 |
|------|----------|------|
| 资产数 < 20 | 'SLSQP' | 精度高，计算时间可接受 |
| 资产数 20-100 | 'CDD' | 速度快，结果准确 |
| 资产数 > 100 | 'CDD' | 必须使用快速算法 |
| 高频调仓 | 'CDD' | 减少计算时间 |

### 4. 风险管理

```python
# 设置合理的权重边界
strategy = RiskParityStrategy(
    lookback=60,
    method='SLSQP'
)

# 在优化器中设置权重限制
optimizer = RiskParityOptimizer(
    method='SLSQP',
    weight_bounds=(0, 0.3)  # 单个资产最大 30%
)
```

希望这个快速参考表能帮助你高效使用代码！