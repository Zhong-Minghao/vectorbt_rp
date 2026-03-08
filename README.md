# Portfolio Backtest Framework

<div align="center">

**一个可扩展的投资组合回测框架**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

基于 vectorbt 构建的高性能回测框架，支持多种投资组合策略，易于扩展和维护。

[快速开始](#-快速开始) • [功能特性](#-功能特性) • [文档](#-文档) • [示例](#-示例)

</div>

---

## ✨ 功能特性

### 🎯 核心功能
- **多种策略支持**：风险平价、均值方差等经典策略
- **模块化设计**：风险模型和优化器独立，易于复用和扩展
- **高性能回测**：基于 vectorbt 的快速回测引擎
- **灵活配置**：支持自定义调仓频率、回看窗口等参数

### 🆕 新增功能
- **多种协方差估计方法**：样本协方差、Ledoit-Wolf 收缩、OAS 收缩
- **多种优化算法**：SLSQP、CCD（坐标下降法）
- **风险模型模块**：独立的风险估计组件
- **优化器模块**：可复用的组合优化算法

### 📊 性能优势
| 算法 | 适用场景 | 计算速度 | 稳定性 |
|------|----------|----------|--------|
| **SLSQP** | 资产数 < 20 | 中等 | 高 |
| **CCD** | 资产数 > 20 | 快 | 高 |

---

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/your-username/portfolio_backtest.git
cd portfolio_backtest

# 安装依赖
pip install -r requirements.txt
```

### 5 分钟上手

```python
from portfolio_backtest import BacktestEngine, RiskParityStrategy
from portfolio_backtest.utils import load_price_data

# 1. 加载价格数据
price_df = load_price_data('your_data.csv')

# 2. 创建策略
strategy = RiskParityStrategy(lookback=60, method='CDD')

# 3. 运行回测
engine = BacktestEngine(init_cash=1_000_000)
result = engine.run(strategy, price_df)

# 4. 查看结果
print(f"年化收益率: {result.metrics['annualized_return']:.2%}")
print(f"夏普比率: {result.metrics['sharpe_ratio']:.2f}")
print(f"最大回撤: {result.metrics['max_drawdown']:.2%}")
```

### 🎨 使用更高级的功能

```python
# 使用 Ledoit-Wolf 收缩估计提高稳定性
strategy = RiskParityStrategy(
    lookback=60,
    method='CDD',
    risk_model='ledoit_wolf'  # 🆕 新参数
)

# 或者直接使用底层组件
from portfolio_backtest.optimizer import MeanVarianceOptimizer

optimizer = MeanVarianceOptimizer(objective='max_sharpe')
weights = optimizer.optimize(returns=returns_df)
```

---

## 📚 文档

### 📖 文档导航

| 文档 | 描述 | 适合人群 |
|------|------|----------|
| [📘 使用指南](USAGE_GUIDE.md) | 完整的使用说明和示例 | 所有用户 |
| [📋 快速参考](QUICK_REFERENCE.md) | 参数速查表和常用代码片段 | 开发者 |
| [🏗️ 架构说明](ARCHITECTURE.md) | 系统架构和设计模式 | 想深入理解的设计者 |
| [🔄 重构总结](REFACTORING_SUMMARY.md) | 代码重构详情和迁移指南 | 维护者 |

### 🔑 核心概念

#### 风险模型 (Risk Models)
```python
from portfolio_backtest.risk import CovarianceEstimator

# 选择合适的协方差估计方法
estimator = CovarianceEstimator(
    method='ledoit_wolf',  # 'sample', 'ledoit_wolf', 'oracle_approximating'
    annualize=True
)
cov_matrix = estimator.estimate_risk(returns)
```

#### 优化器 (Optimizers)
```python
from portfolio_backtest.optimizer import RiskParityOptimizer

# 风险平价优化
optimizer = RiskParityOptimizer(method='CDD')
weights = optimizer.optimize(cov_matrix=cov_matrix)
```

---

## 💡 示例

### 示例 1: 多资产风险平价组合

```python
from portfolio_backtest import BacktestEngine, RiskParityStrategy

# 创建策略
strategy = RiskParityStrategy(
    lookback=60,
    rebalance_freq='ME',  # 月末调仓
    method='CDD',         # 使用快速算法
    risk_model='ledoit_wolf'  # 更稳定的协方差估计
)

# 运行回测
engine = BacktestEngine(init_cash=10_000_000)
result = engine.run(strategy, price_df)

# 分析结果
result.portfolio.stats()
```

### 示例 2: 策略对比

```python
# 定义多个策略进行对比
strategies = [
    RiskParityStrategy(lookback=60, method='SLSQP'),
    RiskParityStrategy(lookback=60, method='CDD'),
    RiskParityStrategy(lookback=60, method='SLSQP', risk_model='ledoit_wolf'),
]

comparison = engine.compare_strategies(
    strategies=strategies,
    names=['RP-SLSQP', 'RP-CDD', 'RP-LW']
)
print(comparison)
```

### 示例 3: 自定义优化目标

```python
from portfolio_backtest.optimizer import MeanVarianceOptimizer

# 目标：年化收益 8% 下最小化方差
optimizer = MeanVarianceOptimizer(
    objective='target_return',
    target_return=0.08,
    weight_bounds=(0, 0.4)  # 单个资产最大权重 40%
)

weights = optimizer.optimize(
    returns=returns_df,
    cov_matrix=cov_matrix,
    mean_returns=mean_returns
)
```

更多示例请查看 [使用指南](USAGE_GUIDE.md)。

---

## 📁 项目结构

```
portfolio_backtest/
├── engine/              # 回测引擎
│   └── backtest.py     # BacktestEngine, BacktestResult
├── strategies/          # 投资组合策略
│   ├── base.py         # 策略基类
│   ├── risk_parity.py  # 风险平价策略
│   └── mean_variance.py # 均值方差策略
├── risk/               # 🆕 风险模型模块
│   ├── base.py         # 风险模型基类
│   ├── covariance.py   # 协方差矩阵估计
│   └── shrinkage.py    # 协方差收缩方法
├── optimizer/          # 🆕 优化器模块
│   ├── base.py         # 优化器基类
│   ├── optimizers.py   # 主要优化算法
│   └── ccd.py          # CCD 算法实现
├── utils/              # 工具函数
│   └── helpers.py      # 数据加载和处理
└── visualization/      # 可视化工具
    └── plots.py        # 绘图函数
```

---

## 🛠️ 技术栈

- **Python 3.8+**
- **vectorbt** - 高性能回测引擎
- **pandas** - 数据处理
- **numpy** - 数值计算
- **scipy** - 优化算法

---

## 📈 性能对比

### 风险平价算法对比

| 指标 | SLSQP | CCD |
|------|-------|-----|
| 计算时间（10000次） | ~2.5秒 | ~0.8秒 |
| 精度 | 高 | 高 |
| 最大差异 | < 0.0001 | - |
| 适用资产数 | < 20 | 无限制 |

### 协方差估计方法对比

| 方法 | 稳定性 | 适用场景 |
|------|--------|----------|
| sample | 中 | 资产数 < 10 |
| ledoit_wolf | 高 | 资产数 10-50 |
| oracle_approximating | 高 | 高斯分布数据 |

---

## 🤝 贡献

欢迎贡献！请随时提交 Pull Request。

### 开发路线图

- [ ] 支持更多风险模型（因子模型、DCC 等）
- [ ] 添加更多优化算法（凸优化、启发式算法）
- [ ] 实现动态权重调整策略
- [ ] 添加更多性能指标和可视化
- [ ] 支持实时数据和交易接口

---

## 📄 License

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📞 联系方式

- **Issue**: 在 GitHub 上提交问题
- **讨论**: 欢迎在 Issues 中讨论功能建议

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐️**

Made with ❤️ by Portfolio Backtest Team

</div>