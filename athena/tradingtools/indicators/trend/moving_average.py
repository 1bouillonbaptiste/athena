import numpy as np
import pandas as pd
from ta.trend import EMAIndicator, SMAIndicator
from pydantic import Field


def simple_moving_average(
    array: list[float] | np.ndarray | pd.Series, window_size: int = Field(ge=1)
) -> np.ndarray:
    """Calculate the Simple Moving Average of input array.

    Each element of the output array is the mean of the previous N elements.
    The first N elements cannot be computed, so they are fixed at the N-th value.

    Args:
        array: 1D collection of price data
        window_size: rolling parameter

    Returns:
        SMA of input array as a numpy array
    """
    return (
        SMAIndicator(pd.Series(array), window_size).sma_indicator().bfill().to_numpy()
    )


def exponential_moving_average(
    array: list[float] | np.ndarray | pd.Series, window_size: int = Field(ge=1)
) -> np.ndarray:
    """Calculate the Exponential Moving Average of input array.

    In an EMA, y_t+1 = alpha * y_t + (1 - alpha) * y_t-1, with alpha = 2 / (window_size + 1).

    Args:
        array: 1D collection of price data
        window_size: rolling parameter

    Returns:
        EMA of input array as a numpy array
    """
    return (
        EMAIndicator(pd.Series(array), window_size).ema_indicator().bfill().to_numpy()
    )
