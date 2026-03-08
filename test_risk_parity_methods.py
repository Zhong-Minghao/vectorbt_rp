"""
测试风险平价的SLSQP和CDD算法

## 风险平价算法对比

### SLSQP (Sequential Least Squares Programming)
- **原理**: 通过优化算法最小化风险贡献的方差
- **优点**: 结果稳定，可复现，适用于各种约束条件
- **缺点**: 计算速度相对较慢，需要设置初始值

### CDD (Cyclical Coordinate Descent)
- **原理**: 基于Spinu (2013)的坐标下降算法，循环更新每个资产的权重
- **优点**: 收敛速度快，对初始值不敏感，有理论收敛保证
- **缺点**: 对于复杂约束条件的处理较为困难

### 验证方法
1. **权重对比**: 比较两种方法计算出的权重差异
2. **回测表现**: 对比两种方法的实际回测表现
3. **风险贡献验证**: 确保风险贡献相等（每个资产的风险贡献应该接近相等）
"""
import sys
sys.path.insert(0, '.')

import numpy as np
import pandas as pd
import time
from portfolio_backtest.optimizer.optimizers import RiskParityOptimizer

def test_algorithms():
    """测试两种算法的结果"""
    print("="*80)
    print("风险平价算法测试")
    print("="*80)

    # 测试案例1: 对角协方差矩阵（理论解：等权重）
    print("\n测试案例1: 独立同方差资产")
    print("-"*80)
    n_assets = 5
    simple_cov = np.eye(n_assets) * 0.01

    # 使用新的优化器模块
    optimizer_slssp = RiskParityOptimizer(method='SLSQP')
    optimizer_cdd = RiskParityOptimizer(method='CDD')

    w_slssp = optimizer_slssp.optimize(cov_matrix=simple_cov)
    w_cdd = optimizer_cdd.optimize(cov_matrix=simple_cov)

    print(f"SLSQP权重: {np.round(w_slssp, 4)}")
    print(f"CDD权重:   {np.round(w_cdd, 4)}")
    print(f"最大差异:  {np.max(np.abs(w_slssp - w_cdd)):.8f}")

    # 测试案例2: 相关资产
    print("\n测试案例2: 相关资产")
    print("-"*80)
    correlated_cov = np.array([
        [0.04, 0.01, 0.005, 0.002, 0.001],
        [0.01, 0.03, 0.008, 0.003, 0.002],
        [0.005, 0.008, 0.025, 0.004, 0.001],
        [0.002, 0.003, 0.004, 0.02, 0.001],
        [0.001, 0.002, 0.001, 0.001, 0.015]
    ])

    start = time.time()
    for _ in range(10000):
        w_slssp2 = optimizer_slssp.optimize(cov_matrix=correlated_cov)
    end = time.time()
    print("SLSQP平均计算时间: {:.4f}秒".format((end - start) / 1000))
    start = time.time()
    for _ in range(10000):
        w_cdd2 = optimizer_cdd.optimize(cov_matrix=correlated_cov)
    end = time.time()
    print("CDD平均计算时间: {:.4f}秒".format((end - start) / 1000))

    print(f"SLSQP权重: {np.round(w_slssp2, 4)}")
    print(f"CDD权重:   {np.round(w_cdd2, 4)}")
    print(f"最大差异:  {np.max(np.abs(w_slssp2 - w_cdd2)):.8f}")

    # 验证风险贡献相等性
    print("\n验证风险贡献相等性:")
    print("-"*80)

    def check_risk_parity(weights, cov_matrix, n):
        """检查风险贡献是否相等"""
        portfolio_vol = np.sqrt(weights.T @ cov_matrix @ weights)
        risk_contributions = weights * (cov_matrix @ weights) / portfolio_vol
        percentage_rc = risk_contributions / portfolio_vol * 100

        print(f"组合波动率: {portfolio_vol:.6f}")
        print(f"风险贡献百分比: {np.round(percentage_rc, 2)}%")
        print(f"目标风险贡献: {100/n:.2f}%")
        print(f"标准差: {np.std(percentage_rc):.4f}%")
        print(f"最大偏差: {np.max(np.abs(percentage_rc - 100/n)):.4f}%")

    print("\nSLSQP方法:")
    check_risk_parity(w_slssp2, correlated_cov, n_assets)

    print("\nCDD方法:")
    check_risk_parity(w_cdd2, correlated_cov, n_assets)

    print("\n" + "="*80)
    print("测试完成！")
    print("="*80)

if __name__ == "__main__":
    test_algorithms()
