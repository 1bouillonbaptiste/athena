from functools import partial
from typing import Any

from jedi.inference.gradual.typing import Callable

from athena.tradingtools.indicators.momentum.rsi import rsi, stochastic_rsi
from athena.tradingtools.indicators.trend.ichimoku import ichimoku
from athena.tradingtools.indicators.trend.macd import macd
from athena.tradingtools.indicators.trend.moving_average import (
    exponential_moving_average,
    simple_moving_average,
)

TECHNICAL_INDICATORS = {
    "exponential_moving_average": exponential_moving_average,
    "ichimoku": ichimoku,
    "macd": macd,
    "rsi": rsi,
    "simple_moving_average": simple_moving_average,
    "stochastic_rsi": stochastic_rsi,
}


def build_indicator(name: str, parameters: dict[str, Any]) -> Callable:
    """Build a function that can be applied of any kind of data.

    Args:
        name: name of the indicator to build, should be in TECHNICAL_INDICATORS
        parameters: set of parameters to build the indicator

    Returns:
        indicator function, is usually applied on market data

    Raises:
        NotImplementedError: if the indicator name is unknown
    """
    if name not in TECHNICAL_INDICATORS:
        raise NotImplementedError(f"Indicator `{name}` is currently not implemented.")

    return partial(TECHNICAL_INDICATORS[name], **parameters)
