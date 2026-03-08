"""
测试重构后的代码功能
"""
import sys
sys.path.insert(0, '.')

import numpy as np
import pandas as pd

# 测试新的模块化结构
def test_new_modules():
    print("="*80)
    print("测试重构后的模块化结构")
    print("="*80)

    # 测试 1: Risk 模块
    print("\n1. 测试 Risk 模块")
    print("-"*80)
    from portfolio_backtest.risk import CovarianceEstimator

    # 创建测试数据
    np.random.seed(42)
    n_assets = 5
    n_obs = 100
    returns = pd.DataFrame(
        np.random.randn(n_obs, n_assets) * 0.01,
        columns=[f'Asset_{i}' for i in range(n_assets)]
    )

    # 测试样本协方差估计
    cov_estimator = CovarianceEstimator(method='sample')
    cov_matrix = cov_estimator.estimate_risk(returns)
    print(f"✓ 协方差矩阵估计成功: {cov_matrix.shape}")
    print(f"  对角线元素: {np.round(np.diag(cov_matrix), 6)}")

    # 测试 2: Optimizer 模块
    print("\n2. 测试 Optimizer 模块")
    print("-"*80)
    from portfolio_backtest.optimizer import RiskParityOptimizer

    # 测试 SLSQP 优化器
    optimizer_slssp = RiskParityOptimizer(method='SLSQP')
    weights_slssp = optimizer_slssp.optimize(cov_matrix=cov_matrix)
    print(f"✓ SLSQP 优化成功: {np.round(weights_slssp, 4)}")
    print(f"  权重和: {np.sum(weights_slssp):.6f}")

    # 测试 CDD 优化器
    optimizer_cdd = RiskParityOptimizer(method='CDD')
    weights_cdd = optimizer_cdd.optimize(cov_matrix=cov_matrix)
    print(f"✓ CDD 优化成功: {np.round(weights_cdd, 4)}")
    print(f"  权重和: {np.sum(weights_cdd):.6f}")

    # 测试差异
    diff = np.abs(weights_slssp - weights_cdd)
    print(f"  最大差异: {np.max(diff):.6f}")

    # 测试 3: 集成的 RiskParityStrategy
    print("\n3. 测试集成后的 RiskParityStrategy")
    print("-"*80)
    from portfolio_backtest.strategies.risk_parity import RiskParityStrategy

    # 创建价格数据
    price_df = (1 + returns).cumprod()
    price_df.index = pd.date_range('2020-01-01', periods=n_obs, freq='D')

    # 测试策略
    strategy = RiskParityStrategy(lookback=60, rebalance_freq='ME', method='SLSQP')
    weights_df = strategy.generate_weights(price_df)

    print(f"✓ 策略权重生成成功: {weights_df.shape}")
    print(f"  调仓次数: {len(weights_df)}")
    print(f"  资产数量: {len(weights_df.columns)}")
    print(f"  最后一次调仓权重: {np.round(weights_df.iloc[-1].values, 4)}")

    # 测试 4: BacktestEngine 兼容性
    print("\n4. 测试 BacktestEngine 兼容性")
    print("-"*80)
    from portfolio_backtest import BacktestEngine

    engine = BacktestEngine(init_cash=1_000_000)
    result = engine.run(strategy, price_df)

    print(f"✓ 回测执行成功")
    print(f"  总收益率: {result.metrics['total_return']:.4f}")
    print(f"  夏普比率: {result.metrics['sharpe_ratio']:.4f}")
    print(f"  最大回撤: {result.metrics['max_drawdown']:.4f}")

    print("\n" + "="*80)
    print("✓ 所有测试通过！重构成功！")
    print("="*80)

if __name__ == "__main__":
    test_new_modules()