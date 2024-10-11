from typing import Self

from athena.core.fluctuations import Fluctuations
from athena.tradingtools import Strategy


class StrategyOptimizer:
    """Take a strategy and optimize it to find the best parameters' combination.

    Args:
        strategy: the strategy to be optimized.
    """

    def __init__(self, strategy: Strategy) -> Self:
        self.strategy = strategy

    def optimize(self, fluctuations: Fluctuations) -> dict:
        """Find the parameters that maximizes the trading performances of the strategy on fluctuations.

        Args:
            fluctuations: market data to calculate trading performance from

        Returns:
            best parameters as a dict
        """
        pass
