from pydantic import Field
from ta.trend import IchimokuIndicator

from athena.core.fluctuations import Fluctuations
from athena.tradingtools.indicators.common import IndicatorLine


def ichimoku(
    fluctuations: Fluctuations,
    window_a: int = Field(ge=1),
    window_b: int = Field(ge=1),
    window_c: int = Field(ge=1),
) -> tuple[IndicatorLine, IndicatorLine, IndicatorLine, IndicatorLine]:
    """Calculate ICHIMOKU cloud.

    The base and conversion lines are respectively long and short term momentum lines.
    The span A  line is the average between the two above lines.
    The span B line is the long term resistances.

    source : https://www.investopedia.com/terms/i/ichimoku-cloud.asp

    Args:
        fluctuations: market data
        window_a: rolling parameter for the 'conversion' line
        window_b: rolling parameter for the 'base' line
        window_c: rolling parameter for the long term resistance line (span B)

    Returns:
        senkou span A as a numpy array
        senkou span B as a numpy array
        kijun-sen (or base) as a numpy array
        tenkan-sen (or conversion) as a numpy array
    """

    ichimoku_indicator = IchimokuIndicator(
        high=fluctuations.get_series("high"),
        low=fluctuations.get_series("low"),
        window1=window_a,
        window2=window_b,
        window3=window_c,
    )

    return (
        IndicatorLine(
            name="span_a", values=ichimoku_indicator.ichimoku_a().bfill().to_numpy()
        ),
        IndicatorLine(
            name="span_b", values=ichimoku_indicator.ichimoku_b().bfill().to_numpy()
        ),
        IndicatorLine(
            name="base",
            values=ichimoku_indicator.ichimoku_base_line().bfill().to_numpy(),
        ),
        IndicatorLine(
            name="conversion",
            values=ichimoku_indicator.ichimoku_conversion_line().bfill().to_numpy(),
        ),
    )
