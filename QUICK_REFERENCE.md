# 快速参考表

## 🎯 根据需求快速找到功能

### 我想...

| 需求 | 使用方法 | 代码示例 |
|------|----------|----------|
| 运行基本风险平价回测 | `RiskParityStrategy` | `strategy = RiskParityStrategy(lookback=60)` |
| 使用更快的优化算法 | 设置 `method='CDD'` | `RiskParityStrategy(method='CDD')` |
| 使用更稳定的协方差估计 | 设置 `risk_model='ledoit_wolf'` | `RiskParityStrategy(risk_model='ledoit_wolf')` |
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