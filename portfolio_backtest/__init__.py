"""
Portfolio Backtest Framework
一个可扩展的投资组合回测框架
"""

from .engine.backtest import BacktestEngine
from .strategies.base import BaseStrategy
from .strategies.risk_parity import RiskParityStrategy
from .strategies.mean_variance import MeanVarianceStrategy

# 新增模块
from .risk import CovarianceEstimator, BaseRiskModel
from .optimizer import BaseOptimizer, RiskParityOptimizer, MeanVarianceOptimizer

__version__ = "1.0.0"
__all__ = [
    "BacktestEngine", "BaseStrategy",
    "RiskParityStrategy", "MeanVarianceStrategy",
    "CovarianceEstimator", "BaseRiskModel",
    "BaseOptimizer", "RiskParityOptimizer", "MeanVarianceOptimizer"
]
