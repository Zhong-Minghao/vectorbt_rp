# 更新日志

## [1.4.0] - 2026-03-16

### 🔥 新增核心功能

#### 调仓有效性分析
全新的精细调仓质量评估方法！

**用户痛点：**
- 现有的 `compare_dynamic_vs_buyhold()` 无法有效评估单次调仓决策
- 需要直接量化"加仓涨了/减仓跌了"这种正确决策的比例
- 想要知道每次调仓决策是否正确

**核心公式：**
```
单次调仓有效性 = (新权重 - 旧权重) × (期间收益率)
```

**逻辑设计：**
- ✅ 正值（>0）：加仓且涨了，或减仓且跌了 → 正确决策
- ❌ 负值（<0）：加仓但跌了，或减仓但涨了 → 错误决策

**输出指标：**
1. **正确率**：正确决策占总调仓次数的比例
2. **累乘结果**：`∏(1 + 单次调仓有效性)`，类似复利
3. **可视化图表**：
   - 上方：每次调仓的柱状图（绿色=正确，红色=错误）
   - 下方：累计乘积曲线（展示整体效果）

**使用方法：**
```python
from portfolio_backtest.visualization import BacktestVisualizer

viz = BacktestVisualizer(result)

# 分析调仓有效性
viz.plot_rebalancing_effectiveness(
    price_df,
    asset_name='SGE黄金9999'
)
```

**应用价值：**
- 🎯 **直接评估决策质量**：不再依赖整体收益，直接看每次决策
- 📊 **量化正确率**：例如"70%的调仓决策是正确的"
- 💡 **优化策略参数**：根据分析结果调整 `lookback` 和 `rebalance_freq`
- 🔍 **找出问题资产**：识别哪些资产的调仓效果不佳

### 📝 文档更新

- ✅ 更新了 [portfolio_backtest/visualization/plots.py](portfolio_backtest/visualization/plots.py)
  - 添加 `_calculate_effectiveness()` 私有方法
  - 添加 `plot_rebalancing_effectiveness()` 公共方法

- ✅ 更新了 [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
  - 在"我想..."表格中添加调仓有效性分析快速入口 🔥
  - 添加详细的使用说明、公式原理、评估标准

- ✅ 创建了 [examples/rebalancing_effectiveness_example.py](examples/rebalancing_effectiveness_example.py)
  - 5 个完整的使用示例
  - 公式原理详解
  - 统计报告生成

### 💡 使用示例

详细示例请查看：
- [examples/rebalancing_effectiveness_example.py](examples/rebalancing_effectiveness_example.py) - 完整代码示例
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md#-调仓有效性分析精细评估) - 快速参考

---

## [1.3.0] - 2026-03-16

### 🆕 新增功能

#### 动态调仓 vs 买入持有对比分析
新增 `compare_dynamic_vs_buyhold()` 函数，解决调仓效果评估难题！

**核心问题：**
- 如何评估动态调仓策略是否比简单买入持有更有效？
- 仓位变化图难以直观判断调仓合理性
- 不同权重下难以直接比较收益

**解决方案：**
```python
viz.compare_dynamic_vs_buyhold(
    price_df,
    asset_name='股票',
    initial_investment=10000
)
```

**功能特点：**
- 📊 直接对比动态调仓 vs 买入持有的价值变化
- 🎯 计算并显示超额收益（调仓是否有效）
- 📍 标注重要调仓时点
- 💡 自动评估调仓质量

**图表包含：**
- 动态调仓策略曲线（蓝色实线）
- 买入持有策略曲线（橙色虚线）
- 调仓时点标注（灰色虚线）
- 详细收益对比（标题显示）

**应用场景：**
- 评估调仓策略的有效性
- 优化调仓频率和参数
- 对比不同资产的表现
- 生成投资决策报告

### 📝 文档更新

- ✅ 更新了 [portfolio_backtest/visualization/plots.py](portfolio_backtest/visualization/plots.py)
  - 添加 `compare_dynamic_vs_buyhold()` 方法
  - 完整的参数说明和使用示例

- ✅ 更新了 [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
  - 在"我想..."表格中添加对比分析快速入口
  - 添加详细的使用说明和解读指南

- ✅ 创建了 [examples/dynamic_vs_buyhold_example.py](examples/dynamic_vs_buyhold_example.py)
  - 5 个完整的使用示例
  - 涵盖各种分析场景

### 💡 使用示例

详细示例请查看：
- [examples/dynamic_vs_buyhold_example.py](examples/dynamic_vs_buyhold_example.py) - 完整代码示例
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md#-对比动态调仓-vs-买入持有) - 快速参考

---

## [1.2.0] - 2026-03-16

### 🆕 新增功能

#### 改进的资产分析可视化
`plot_assets_and_weights()` 函数全面升级！

**之前的功能：**
- 显示所有资产的价格走势和权重变化（两个子图）
- 只能按 `top_n` 参数选择权重最大的 N 个资产

**现在的功能：**
- ✨ 单一资产深度分析（价格 + 权重叠加显示）
- 📊 双 y 轴设计：左侧价格，右侧权重
- 🎨 价格折线图 + 权重柱状图（带透明度）
- 🎯 灵活的参数配置

**新的参数：**
```python
viz.plot_assets_and_weights(
    price_df,
    asset_name='黄金',        # 指定资产（None=自动选择权重最大的）
    freq='W',                 # 权重显示频率
    normalize_price=True,     # 是否归一化价格
    weight_alpha=0.3          # 权重柱状图透明度 (0-1)
)
```

**应用场景：**
- 📈 分析单个资产的历史走势
- 💼 观察策略对该资产的加减仓时机
- 🎯 理解策略的交易逻辑
- 📊 评估仓位调整的合理性

### 📝 文档更新

- ✅ 更新了 [portfolio_backtest/visualization/plots.py](portfolio_backtest/visualization/plots.py)
  - 重写了 `plot_assets_and_weights()` 方法
  - 添加了详细的参数说明

- ✅ 更新了 [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
  - 在"我想..."表格中添加资产分析快速入口
  - 添加资产分析使用示例

- ✅ 创建了 [examples/asset_weight_analysis_example.py](examples/asset_weight_analysis_example.py)
  - 5 个完整的使用示例
  - 涵盖各种应用场景

### 💡 使用示例

详细示例请查看：
- [examples/asset_weight_analysis_example.py](examples/asset_weight_analysis_example.py) - 完整代码示例
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md#-资产价格与仓位分析) - 快速参考

---

## [1.1.0] - 2026-03-15

### 🆕 新增功能

#### 自定义风险预算
`RiskParityStrategy` 现在支持自定义风险预算功能！

**之前的行为：**
```python
# 只能实现等风险贡献
strategy = RiskParityStrategy(lookback=60)
# 每个资产承担相同的风险（1/n）
```

**现在的功能：**
```python
import numpy as np

# 自定义每个资产的风险贡献目标
custom_budget = np.array([0.6, 0.4])  # 资产1承担60%风险，资产2承担40%风险
strategy = RiskParityStrategy(
    lookback=60,
    risk_budget=custom_budget  # 🆕 新参数
)
```

### 📚 应用场景

1. **保守型 vs 激进型配置**
   ```python
   # 保守型：让债券等低风险资产承担更多风险预算
   conservative_budget = np.array([0.3, 0.5, 0.2])
   strategy_conservative = RiskParityStrategy(risk_budget=conservative_budget)

   # 激进型：让股票等高风险资产承担更多风险预算
   aggressive_budget = np.array([0.6, 0.2, 0.2])
   strategy_aggressive = RiskParityStrategy(risk_budget=aggressive_budget)
   ```

2. **行业轮动策略**
   ```python
   # 牛市：超配成长行业
   bull_market_budget = np.array([0.15, 0.30, 0.25, 0.20, 0.10])
   # 金融、科技、消费、医疗、能源

   # 震荡市：均衡配置
   neutral_market_budget = np.array([0.20, 0.20, 0.20, 0.20, 0.20])
   ```

3. **风险因子投资**
   ```python
   # 根据风险因子暴露度分配风险预算
   # 例如：价值因子、动量因子、质量因子等
   factor_budget = np.array([0.4, 0.3, 0.3])
   ```

### 🔧 技术实现

- **参数位置**: `RiskParityStrategy.__init__(risk_budget=None)`
- **参数类型**: `Optional[np.ndarray]`
- **默认值**: `None`（等风险贡献）
- **传递路径**: 策略 → `RiskParityOptimizer`
- **优化算法**: 支持 SLSQP 和 CDD 两种方法

### 📖 文档更新

- ✅ 更新了 [`portfolio_backtest/strategies/risk_parity.py`](portfolio_backtest/strategies/risk_parity.py)
  - 添加 `risk_budget` 参数
  - 更新类和方法文档字符串
  - 添加使用示例

- ✅ 更新了 [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md)
  - 在"我想..."表格中添加自定义风险预算条目
  - 在参数速查表中添加 `risk_budget` 参数说明
  - 添加使用示例代码片段

- ✅ 创建了 [`examples/custom_risk_budget_example.py`](examples/custom_risk_budget_example.py)
  - 4个完整的使用示例
  - 激进 vs 保守策略对比
  - 行业轮动策略示例
  - 风险贡献验证函数

### 🎯 使用示例

详细示例请查看：
- [`examples/custom_risk_budget_example.py`](examples/custom_risk_budget_example.py) - 完整代码示例
- [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) - 快速参考

### ⚡ 性能说明

- 自定义风险预算不会影响计算性能
- 与等风险贡献具有相同的复杂度
- SLSQP 和 CDD 算法都支持

### 🐛 已知问题

无

### 🔜 未来计划

- [ ] 添加动态风险预算调整（根据市场环境自动调整）
- [ ] 支持风险预算约束（如最小/最大风险贡献限制）
- [ ] 添加风险预算优化器（自动寻找最优风险预算分配）

---

## [1.0.0] - 2026-03-10

### 🎉 初始版本

- ✅ 模块化的投资组合回测框架
- ✅ 风险平价策略
- ✅ 均值方差策略
- ✅ 多种协方差估计方法
- ✅ SLSQP 和 CDD 优化算法
- ✅ 完整的文档和示例

---

## 📝 版本说明

版本号格式：`主版本.次版本.修订版本`

- **主版本**：重大架构变更或不兼容的 API 变更
- **次版本**：向后兼容的新功能
- **修订版本**：向后兼容的问题修复

**当前版本**: 1.1.0