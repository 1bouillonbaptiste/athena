from ta.momentum import RSIIndicator, StochRSIIndicator

from athena.core.fluctuations import Fluctuations
from athena.tradingtools.indicators.common import IndicatorLine


def rsi(fluctuations: Fluctuations, window_size: int) -> IndicatorLine:
    """Calculate the Relative Strength Index (RSI) of an array of prices.

    Args:
        fluctuations: market data
        window_size: rolling parameter

    Returns:
        rsi line as a numpy array
    """
    return IndicatorLine(
        name="rsi",
        values=RSIIndicator(close=fluctuations.get_series("close"), window=window_size)
        .rsi()
        .bfill()
        .to_numpy(),
    )


def stochastic_rsi(
    fluctuations: Fluctuations, window_size: int, smooth_k: int, smooth_d: int
) -> tuple[IndicatorLine, IndicatorLine, IndicatorLine]:
    """Calculate the Stochastic Relative Strength Index of an array of prices.

    The RSI is calculated using the window_size.
    The high and low RSI lines are the highest / lowest RSI in a range of window_size.
    The stochastic RSI is the difference between RSI line and low, divided by the difference between high and low.
    The stochastic RSI %K is the average of RSI line in a range of smooth_k.
    The stochastic RSI %D is the average of RSI line in a range of smooth_d.

    Args:
        fluctuations: market data
        window_size: rolling parameter
        smooth_k: smoothing parameter
        smooth_d: smoothing parameter

    Returns:
    """

    rsi_indicator = StochRSIIndicator(
        close=fluctuations.get_series("close"),
        window=window_size,
        smooth1=smooth_k,
        smooth2=smooth_d,
    )
    return (
        IndicatorLine(
            name="stochastic_rsi", values=rsi_indicator.stochrsi().bfill().to_numpy()
        ),
        IndicatorLine(
            name="stochastic_rsi_k",
            values=rsi_indicator.stochrsi_k().bfill().to_numpy(),
        ),
        IndicatorLine(
            name="stochastic_rsi_d",
            values=rsi_indicator.stochrsi_d().bfill().to_numpy(),
        ),
    )
