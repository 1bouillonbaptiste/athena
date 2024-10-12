from typing import Any

from athena.tradingtools.strategies.dca import StrategyDCA, StrategyDCAModel

STRATEGIES_MATCH = {"strategy_dca": StrategyDCA}
CONFIGS_MATCH = {"strategy_dca": StrategyDCAModel}


def init_strategy(strategy_name: str, strategy_params: dict[str:Any]):
    """Build a Strategy object."""
    config = CONFIGS_MATCH[strategy_name].model_validate(strategy_params)
    return STRATEGIES_MATCH[strategy_name](config=config)
