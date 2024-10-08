from pydantic import Field
from ta.trend import EMAIndicator, SMAIndicator

from athena.core.interfaces import Fluctuations
from athena.tradingtools.indicators.common import IndicatorLine


def simple_moving_average(
    fluctuations: Fluctuations, window_size: int = Field(ge=1), column: str = "close"
) -> IndicatorLine:
    """Calculate the Simple Moving Average of input array.

    Each element of the output array is the mean of the previous N elements.
    The first N elements cannot be computed, so they are fixed at the N-th value.

    Args:
        fluctuations: market data
        window_size: rolling parameter
        column: which column to take for moving average

    Returns:
        SMA of input array as a numpy array
    """
    return IndicatorLine(
        name="simple_moving_average",
        values=SMAIndicator(fluctuations.get_series(attribute_name=column), window_size)
        .sma_indicator()
        .bfill()
        .to_numpy(),
    )


def exponential_moving_average(
    fluctuations: Fluctuations, window_size: int = Field(ge=1), column: str = "close"
) -> IndicatorLine:
    """Calculate the Exponential Moving Average of input array.

    In an EMA, y_t+1 = alpha * y_t + (1 - alpha) * y_t-1, with alpha = 2 / (window_size + 1).

    Args:
        fluctuations: market data
        window_size: rolling parameter
        column: which column to take for moving average

    Returns:
        EMA of input array as a numpy array
    """
    return IndicatorLine(
        name="exponential_moving_average",
        values=EMAIndicator(fluctuations.get_series(attribute_name=column), window_size)
        .ema_indicator()
        .bfill()
        .to_numpy(),
    )
