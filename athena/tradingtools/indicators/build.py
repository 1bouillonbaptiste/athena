from typing import Callable

from collections.abc import Iterable

from athena.core.config import IndicatorsConfig
from athena.core.interfaces import Fluctuations
from athena.tradingtools.indicators import build_indicator


def build_indicator_lines(
    config: IndicatorsConfig, fluctuations: Fluctuations
) -> list[Callable]:
    """Build indicators lines from a configuration.

    Args:
        config: indicators configuration.
        fluctuations: market data

    Returns:
        indicator lines as a list
    """
    indicators_lines = []
    for indicator_config in config.indicators:
        indicator_function = build_indicator(
            name=indicator_config.name, parameters=indicator_config.parameters
        )
        new_indicators_lines = indicator_function(fluctuations)
        if isinstance(new_indicators_lines, Iterable):
            indicators_lines.extend(new_indicators_lines)
        else:
            indicators_lines.append(new_indicators_lines)

    return indicators_lines
