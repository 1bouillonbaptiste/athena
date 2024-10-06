import numpy as np
import pandas as pd
from ta.trend import MACD

from athena.tradingtools.indicators.common import PriceCollection


def macd(
    prices: PriceCollection, window_slow: int, window_fast: int, window_signal: int
) -> np.ndarray:
    """Calculate MACD (Moving Average Convergence Divergence) line.

    We calculate the fast and slow moving average from prices.
    The MACD is the difference between the two moving averages, and the signal is the MACD moving average.
    When MACD signal diff is above 0, the price is stronger than the history.
    When MACD signal diff growths, the price is getting stronger and stronger.

    Args:
        prices: collection of prices
        window_slow: rolling parameter for slow MA
        window_fast: rolling parameter for fast MA
        window_signal: rolling parameter for MACD signal

    Returns:
        MACD signal diff as a numpy array
    """
    return (
        MACD(
            close=pd.Series(prices),
            window_slow=window_slow,
            window_fast=window_fast,
            window_sign=window_signal,
        )
        .macd_diff()
        .bfill()
        .to_numpy()
    )
