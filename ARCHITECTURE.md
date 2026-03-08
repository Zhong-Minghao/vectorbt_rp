# 项目架构说明

## 🏗️ 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户应用层                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Jupyter     │  │  Scripts     │  │  其他应用     │          │
│  │  Notebooks   │  │  & Scripts   │  │               │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     portfolio_backtest 包                        │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                        策略层 (strategies/)                │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
│  │  │  Base       │  │  Risk       │  │  Mean       │       │   │
│  │  │  Strategy   │  │  Parity     │  │  Variance   │       │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │   │
│  └─────────┼────────────────┼──────────────────┼──────────────┘   │
│            │                │                  │                  │
│            ▼                ▼                  ▼                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                        业务逻辑层                          │   │
│  │  ┌─────────────────┐        ┌─────────────────┐          │   │
│  │  │  engine/        │        │  visualization/ │          │   │
│  │  │  BacktestEngine │        │  plots.py       │          │   │
│  │  └─────────────────┘        └─────────────────┘          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      核心组件层                            │   │
│  │  ┌──────────────┐              ┌──────────────┐          │   │
│  │  │   risk/      │              │ optimizer/   │          │   │
│  │  │              │              │              │          │   │
│  │  │ ┌──────────┐ │              │ ┌──────────┐ │          │   │
│  │  │ │Covariance│ │              │ │RiskParity│ │          │   │
│  │  │ │Estimator │ │              │ │Optimizer │ │          │   │
│  │  │ └──────────┘ │              │ └──────────┘ │          │   │
│  │  │              │              │              │          │   │
│  │  │ ┌──────────┐ │              │ ┌──────────┐ │          │   │
│  │  │ │Shrinkage │ │              │ │MeanVar   │ │          │   │
│  │  │ │Estimator │ │              │ │Optimizer │ │          │   │
│  │  │ └──────────┘ │              │ └──────────┘ │          │   │
│  │  └──────────────┘              └──────────────┘          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      工具层 (utils/)                       │   │
│  │  数据加载、清理、转换等辅助函数                             │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      第三方依赖库                                 │
│  vectorbt, pandas, numpy, scipy, matplotlib                     │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 数据流图

### 典型的回测流程

```
用户代码
    │
    ├─ 1. 加载价格数据
    │       price_df = load_price_data('data.csv')
    │
    ├─ 2. 创建策略
    │       strategy = RiskParityStrategy(lookback=60)
    │       │
    │       └─ 内部初始化:
    │           ├─ CovarianceEstimator(method='sample')
    │           └─ RiskParityOptimizer(method='SLSQP')
    │
    ├─ 3. 创建回测引擎
    │       engine = BacktestEngine(init_cash=1_000_000)
    │
    └─ 4. 运行回测
            result = engine.run(strategy, price_df)
                │
                ├─ 3.1. 清理数据
                │       price_df = clean_price_data(price_df)
                │
                ├─ 3.2. 生成权重
                │       weights = strategy.generate_weights(price_df)
                │           │
                │           └─ 对每个调仓日:
                │               ├─ 计算协方差
                │               │   cov = cov_estimator.estimate_risk(returns)
                │               │
                │               └─ 优化权重
                │                   w = optimizer.optimize(cov_matrix=cov)
                │
                ├─ 3.3. 扩展权重到每日
                │       daily_weights = weights.reindex(price_df.index).ffill()
                │
                ├─ 3.4. 运行 vectorbt 回测
                │       portfolio = vbt.Portfolio.from_orders(...)
                │
                └─ 3.5. 计算性能指标
                        metrics = calculate_metrics(portfolio)

    └─ 5. 分析结果
            print(result.metrics)
            result.portfolio.plot()
```

## 🧩 模块关系图

### Risk 模块

```
BaseRiskModel (抽象基类)
    │
    └─ CovarianceEstimator
        ├─ method: 'sample' (样本协方差)
        ├─ method: 'ledoit_wolf' (Ledoit-Wolf 收缩)
        └─ method: 'oracle_approximating' (OAS 收缩)

    └─ ShrinkageEstimator
        ├─ shrinkage_type: 'constant_correlation'
        ├─ shrinkage_type: 'single_factor'
        └─ shrinkage_type: 'identity'
```

### Optimizer 模块

```
BaseOptimizer (抽象基类)
    │
    ├─ RiskParityOptimizer
    │   ├─ method: 'SLSQP' (序列二次规划)
    │   └─ method: 'CDD' (坐标下降法)
    │
    └─ MeanVarianceOptimizer
        ├─ objective: 'max_sharpe' (最大化夏普比率)
        ├─ objective: 'min_variance' (最小化方差)
        └─ objective: 'target_return' (目标收益优化)
```

### Strategy 模块

```
BaseStrategy (抽象基类)
    │
    ├─ RiskParityStrategy
    │   ├─ 使用: CovarianceEstimator + RiskParityOptimizer
    │   └─ 目标: 等风险贡献组合
    │
    └─ MeanVarianceStrategy
        ├─ 使用: 协方差 + 收益率预测
        └─ 目标: 最优风险收益组合
```

## 🎨 设计模式

### 1. 策略模式 (Strategy Pattern)
```python
# 不同的优化算法可以互换使用
optimizer = RiskParityOptimizer(method='SLSQP')  # 或 'CDD'
weights = optimizer.optimize(cov_matrix=cov)
```

### 2. 模板方法模式 (Template Method Pattern)
```python
# 基类定义算法框架，子类实现具体步骤
class BaseStrategy(ABC):
    def generate_weights(self, price_df, rebalance_mask):
        # 模板方法：定义流程
        price_df = self.validate_data(price_df)
        returns = price_df.pct_change().dropna()
        # ... 具体实现由子类完成
```

### 3. 依赖注入 (Dependency Injection)
```python
# 策略类依赖具体的 risk model 和 optimizer
class RiskParityStrategy:
    def __init__(self, risk_model='sample', method='SLSQP'):
        self.cov_estimator = CovarianceEstimator(method=risk_model)
        self.optimizer = RiskParityOptimizer(method=method)
```

### 4. 工厂模式 (Factory Pattern)
```python
# 通过参数选择不同的实现
def create_optimizer(method):
    if method == 'SLSQP':
        return SLSQPOptimizer()
    elif method == 'CDD':
        return CCDOptimizer()
```

## 🔧 扩展点

### 1. 添加新的风险模型

```python
from portfolio_backtest.risk.base import BaseRiskModel

class FactorRiskModel(BaseRiskModel):
    """因子风险模型"""

    def __init__(self, n_factors=5):
        super().__init__(name=f"Factor Model ({n_factors} factors)")
        self.n_factors = n_factors

    def estimate_risk(self, returns):
        # 1. 估计因子载荷
        # 2. 估计因子协方差
        # 3. 计算特异性风险
        # 4. 组合得到总协方差矩阵
        return cov_matrix

# 使用
strategy = RiskParityStrategy(risk_model='factor')  # 假设扩展支持
```

### 2. 添加新的优化算法

```python
from portfolio_backtest.optimizer.base import BaseOptimizer

class ParticleSwarmOptimizer(BaseOptimizer):
    """粒子群优化算法"""

    def __init__(self, n_particles=30, max_iter=100):
        super().__init__(name="Particle Swarm Optimization")
        self.n_particles = n_particles
        self.max_iter = max_iter

    def optimize(self, cov_matrix, **kwargs):
        # 实现粒子群优化算法
        return optimal_weights

# 使用
optimizer = ParticleSwarmOptimizer()
weights = optimizer.optimize(cov_matrix=cov)
```

### 3. 添加新的策略

```python
from portfolio_backtest.strategies.base import BaseStrategy

class BlackLittermanStrategy(BaseStrategy):
    """Black-Litterman 组合策略"""

    def __init__(self, lookback=60, views=None):
        super().__init__(name="Black-Litterman")
        self.lookback = lookback
        self.views = views

    def generate_weights(self, price_df, rebalance_mask):
        # 1. 计算市场均衡收益
        # 2. 结合投资者观点
        # 3. 优化组合权重
        return weights_df
```

## 📊 性能考虑

### 1. 计算复杂度

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| 样本协方差估计 | O(T×N²) | T: 时间点数, N: 资产数 |
| Ledoit-Wolf 收缩 | O(T×N² + N³) | 额外的收缩参数计算 |
| SLSQP 优化 | O(k×N³) | k: 迭代次数 |
| CDD 优化 | O(k×N²) | 通常比 SLSQP 快 |

### 2. 内存使用

- 协方差矩阵: N×N
- 收益率矩阵: T×N
- 优化器中间变量: O(N²)

### 3. 优化建议

1. **大数据集**: 考虑使用增量更新或近似方法
2. **高频调仓**: 使用 CDD 算法替代 SLSQP
3. **多资产组合**: 考虑因子模型降低协方差矩阵维度

## 🛡️ 错误处理

### 风险模型错误

```python
try:
    cov_matrix = cov_estimator.estimate_risk(returns)
except ValueError as e:
    # 处理协方差矩阵非正定等问题
    print(f"协方差估计失败: {e}")
    # 使用备选方案
    cov_matrix = fallback_estimator.estimate_risk(returns)
```

### 优化器错误

```python
try:
    weights = optimizer.optimize(cov_matrix=cov)
except ValueError as e:
    # 处理优化失败等问题
    print(f"优化失败: {e}")
    # 返回等权重作为备选
    weights = np.ones(n) / n
```

这个架构设计使得代码既保持了简洁性，又具备了强大的扩展能力！