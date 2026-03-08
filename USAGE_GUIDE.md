# 快速使用指南

## 🚀 快速开始

### 1. 基本回测（与之前完全相同）

```python
from portfolio_backtest import BacktestEngine, RiskParityStrategy
from portfolio_backtest.utils import load_price_data

# 加载数据
price_df = load_price_data('your_data.csv')

# 创建策略
strategy = RiskParityStrategy(lookback=60, method='SLSQP')

# 运行回测
engine = BacktestEngine(init_cash=1_000_000)
result = engine.run(strategy, price_df)

# 查看结果
print(result.metrics)
result.portfolio.plot()
```

## 🆕 新功能使用

### 2. 使用不同的风险模型

```python
# 使用 Ledoit-Wolf 收缩估计
strategy = RiskParityStrategy(
    lookback=60,
    method='SLSQP',
    risk_model='ledoit_wolf'  # 🆕 新参数
)

result = engine.run(strategy, price_df)
```

### 3. 直接使用风险模型

```python
from portfolio_backtest.risk import CovarianceEstimator
import pandas as pd

# 创建风险模型
risk_model = CovarianceEstimator(
    method='ledoit_wolf',  # 或 'sample', 'oracle_approximating'
    annualize=True  # 年化处理
)

# 估计协方差矩阵
returns = pd.read_csv('returns.csv', index_col=0)
cov_matrix = risk_model.estimate_risk(returns)

print(f"协方差矩阵形状: {cov_matrix.shape}")
```

### 4. 直接使用优化器

```python
from portfolio_backtest.optimizer import RiskParityOptimizer
import numpy as np

# 创建优化器
optimizer = RiskParityOptimizer(
    method='CDD',  # 或 'SLSQP'
    weight_bounds=(0, 1)  # 权重范围
)

# 准备协方差矩阵
cov_matrix = np.array([[0.04, 0.01], [0.01, 0.03]])

# 优化权重
weights = optimizer.optimize(cov_matrix=cov_matrix)
print(f"最优权重: {weights}")
```

### 5. 均值方差优化

```python
from portfolio_backtest.optimizer import MeanVarianceOptimizer
import pandas as pd

# 加载数据
returns = pd.read_csv('returns.csv', index_col=0)

# 创建优化器 - 最大化夏普比率
optimizer = MeanVarianceOptimizer(
    objective='max_sharpe',
    risk_free_rate=0.03
)

weights = optimizer.optimize(returns=returns)
print(f"最大化夏普比率权重: {weights}")

# 创建优化器 - 最小化方差
optimizer_min_var = MeanVarianceOptimizer(
    objective='min_variance'
)

weights_min_var = optimizer_min_var.optimize(returns=returns)
print(f"最小方差权重: {weights_min_var}")
```

### 6. 自定义风险预算

```python
from portfolio_backtest.optimizer import RiskParityOptimizer
import numpy as np

# 定义自定义风险预算
# 例如：60% 风险给资产1，40% 风险给资产2
custom_budget = np.array([0.6, 0.4])

optimizer = RiskParityOptimizer(
    method='SLSQP',
    risk_budget=custom_budget  # 🆕 自定义风险预算
)

cov_matrix = np.array([[0.04, 0.01], [0.01, 0.03]])
weights = optimizer.optimize(cov_matrix=cov_matrix)
print(f"自定义风险预算权重: {weights}")
```

### 7. 策略对比

```python
from portfolio_backtest import BacktestEngine
from portfolio_backtest.strategies import RiskParityStrategy, MeanVarianceStrategy

# 创建多个策略
strategies = [
    RiskParityStrategy(lookback=60, method='SLSQP'),
    RiskParityStrategy(lookback=60, method='CDD'),
    RiskParityStrategy(lookback=60, method='SLSQP', risk_model='ledoit_wolf'),
    MeanVarianceStrategy(lookback=60)
]

# 对比回测
engine = BacktestEngine(init_cash=1_000_000)
comparison = engine.compare_strategies(
    strategies=strategies,
    names=['RP-SLSQP', 'RP-CDD', 'RP-LW', 'Mean-Var']
)

print(comparison)
```

## 🔧 高级用法

### 8. 分析风险贡献

```python
from portfolio_backtest.strategies.risk_parity import RiskParityStrategy
import numpy as np

strategy = RiskParityStrategy(lookback=60)
weights_df = strategy.generate_weights(price_df)

# 获取最后一次调仓的权重
last_weights = weights_df.iloc[-1].values

# 计算风险贡献（使用策略内置的方法）
cov_matrix = strategy.cov_estimator.estimate_risk(returns)
risk_analysis = strategy.analyze_risk_contributions(
    weights=last_weights,
    cov_matrix=cov_matrix,
    asset_names=price_df.columns.tolist()
)

print(risk_analysis)
```

### 9. 使用 Jupyter Notebook 交互式分析

```python
# 在 Jupyter Notebook 中
import matplotlib.pyplot as plt
from portfolio_backtest import BacktestEngine, RiskParityStrategy
from portfolio_backtest.visualization import plot_weights

# 运行回测
strategy = RiskParityStrategy(lookback=60)
engine = BacktestEngine()
result = engine.run(strategy, price_df)

# 可视化权重变化
plot_weights(result.weights)

# 显示性能指标
result.portfolio.stats()

# 绘制净值曲线
result.portfolio.value().plot()
plt.title('Portfolio Value')
plt.show()
```

### 10. 调试和验证

```python
from portfolio_backtest.optimizer import RiskParityOptimizer
from portfolio_backtest.risk import CovarianceEstimator
import numpy as np

# 创建测试数据
np.random.seed(42)
returns = np.random.randn(100, 5) * 0.01

# 测试风险模型
risk_models = ['sample', 'ledoit_wolf', 'oracle_approximating']
for model in risk_models:
    estimator = CovarianceEstimator(method=model)
    cov = estimator.estimate_risk(returns)
    print(f"{model}: 条件数 = {np.linalg.cond(cov):.2f}")

# 测试优化器一致性
optimizer_slssp = RiskParityOptimizer(method='SLSQP')
optimizer_cdd = RiskParityOptimizer(method='CDD')

cov = CovarianceEstimator(method='sample').estimate_risk(returns)
w_slssp = optimizer_slssp.optimize(cov_matrix=cov)
w_cdd = optimizer_cdd.optimize(cov_matrix=cov)

print(f"\n优化器一致性:")
print(f"SLSQP 权重: {np.round(w_slssp, 4)}")
print(f"CDD 权重:   {np.round(w_cdd, 4)}")
print(f"最大差异:   {np.max(np.abs(w_slssp - w_cdd)):.6f}")
```

## 📊 实际应用示例

### 示例 1: 多资产风险平价组合

```python
from portfolio_backtest import BacktestEngine, RiskParityStrategy
from portfolio_backtest.utils import load_price_data

# 加载多资产价格数据
price_df = load_price_data('multi_asset_prices.csv')

# 创建风险平价策略
strategy = RiskParityStrategy(
    lookback=60,           # 60天回看窗口
    rebalance_freq='ME',   # 月末调仓
    method='CDD',          # 使用快速 CCD 算法
    risk_model='ledoit_wolf'  # 使用更稳定的协方差估计
)

# 运行回测
engine = BacktestEngine(init_cash=10_000_000)
result = engine.run(strategy, price_df)

# 分析结果
print(f"年化收益率: {result.metrics['annualized_return']:.2%}")
print(f"夏普比率: {result.metrics['sharpe_ratio']:.2f}")
print(f"最大回撤: {result.metrics['max_drawdown']:.2%}")
```

### 示例 2: 策略对比和选择

```python
from portfolio_backtest import BacktestEngine
from portfolio_backtest.strategies import RiskParityStrategy, MeanVarianceStrategy

# 定义策略配置
configs = {
    '风险平价-SLSQP': RiskParityStrategy(lookback=60, method='SLSQP'),
    '风险平价-CDD': RiskParityStrategy(lookback=60, method='CDD'),
    '风险平价-LW': RiskParityStrategy(lookback=60, method='SLSQP', risk_model='ledoit_wolf'),
    '均值方差': MeanVarianceStrategy(lookback=60)
}

# 批量回测
results = {}
engine = BacktestEngine(init_cash=1_000_000)

for name, strategy in configs.items():
    try:
        result = engine.run(strategy, price_df)
        results[name] = result.metrics
        print(f"✓ {name} 完成")
    except Exception as e:
        print(f"✗ {name} 失败: {e}")

# 转换为 DataFrame 对比
import pandas as pd
comparison_df = pd.DataFrame(results).T
print("\n策略对比:")
print(comparison_df[['annualized_return', 'sharpe_ratio', 'max_drawdown']])
```

### 示例 3: 自定义优化目标

```python
from portfolio_backtest.optimizer import MeanVarianceOptimizer
from portfolio_backtest.risk import CovarianceEstimator
import numpy as np

# 加载数据
returns = price_df.pct_change().dropna()

# 设置目标年化收益率
target_return = 0.08  # 8%

# 创建优化器
optimizer = MeanVarianceOptimizer(
    objective='target_return',
    target_return=target_return,
    weight_bounds=(0, 0.4)  # 单个资产最大权重 40%
)

# 估计协方差和收益
cov_estimator = CovarianceEstimator(method='ledoit_wolf')
cov_matrix = cov_estimator.estimate_risk(returns)
mean_returns = returns.mean().values * 252  # 年化

# 优化
weights = optimizer.optimize(
    cov_matrix=cov_matrix,
    mean_returns=mean_returns
)

print(f"目标收益 {target_return:.0%} 下的最优权重:")
for asset, weight in zip(price_df.columns, weights):
    print(f"  {asset}: {weight:.2%}")
```

## ⚠️ 常见问题

### Q1: 如何选择协方差估计方法？

**A:**
- **sample**: 适用于资产数较少、数据充足的情况
- **ledoit_wolf**: 适用于资产数较多、需要更稳定估计的情况（推荐）
- **oracle_approximating**: 假设数据服从高斯分布时的最优收缩

### Q2: 如何选择优化算法？

**A:**
- **SLSQP**: 精度高、稳定，但计算较慢
- **CDD**: 速度快、适合大规模问题，推荐用于高频调仓

### Q3: 如何处理优化失败？

**A:**
```python
try:
    weights = optimizer.optimize(cov_matrix=cov_matrix)
except ValueError as e:
    print(f"优化失败: {e}")
    # 使用备选方案
    weights = np.ones(n) / n  # 等权重
```

### Q4: 如何提高回测速度？

**A:**
1. 使用 CDD 算法替代 SLSQP
2. 减少调仓频率（如从周调改为月调）
3. 使用更短的回看窗口
4. 考虑使用增量更新方法

## 📚 更多资源

- [重构总结](REFACTORING_SUMMARY.md) - 了解代码重构详情
- [架构说明](ARCHITECTURE.md) - 深入理解系统架构
- [API 文档](portfolio_backtest/) - 查看 API 文档

祝你使用愉快！如有问题，欢迎反馈。