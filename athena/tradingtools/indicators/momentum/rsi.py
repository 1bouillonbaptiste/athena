import numpy as np
import pandas as pd

from ta.momentum import RSIIndicator, StochRSIIndicator


def rsi(prices: list[float] | np.ndarray | pd.Series, window_size: int) -> np.ndarray:
    """Calculate the Relative Strength Index (RSI) of an array of prices.

    Args:
        prices: collection of prices
        window_size: rolling parameter

    Returns:
        rsi line as a numpy array
    """
    return (
        RSIIndicator(close=pd.Series(prices), window=window_size)
        .rsi()
        .bfill()
        .to_numpy()
    )


def stochastic_rsi(
    prices: list[float], window_size: int, smooth_k: int, smooth_d: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Calculate the Stochastic Relative Strength Index of an array of prices.

    The RSI is calculated using the window_size.
    The high and low RSI lines are the highest / lowest RSI in a range of window_size.
    The stochastic RSI is the difference between RSI line and low, divided by the difference between high and low.
    The stochastic RSI %K is the average of RSI line in a range of smooth_k.
    The stochastic RSI %D is the average of RSI line in a range of smooth_d.

    Args:
        prices: collection of prices
        window_size: rolling parameter
        smooth_k: smoothing parameter
        smooth_d: smoothing parameter

    Returns:
    """

    rsi_indicator = StochRSIIndicator(
        close=pd.Series(prices), window=window_size, smooth1=smooth_k, smooth2=smooth_d
    )
    return (
        rsi_indicator.stochrsi().bfill().to_numpy(),
        rsi_indicator.stochrsi_k().bfill().to_numpy(),
        rsi_indicator.stochrsi_d().bfill().to_numpy(),
    )
