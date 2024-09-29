from typing import Any

from athena.tradingtools.strategies.dca import StrategyDCA

STRATEGIES_MATCH = {"strategy_dca": StrategyDCA}


def init_strategy(strategy_name: str, strategy_params: dict[str:Any]):
    """Build a Strategy object."""
    return STRATEGIES_MATCH[strategy_name](**strategy_params)
