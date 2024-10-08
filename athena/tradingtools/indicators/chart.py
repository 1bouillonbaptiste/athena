from pathlib import Path
from random import randint

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from athena.core.interfaces import Fluctuations
from athena.tradingtools.indicators.common import IndicatorLine

ALL_COLORS = px.colors.named_colorscales()


def _generate_random_rgb():
    """Create a color from random numbers.

    The color value starts at 50 to be light enough.

    Returns:
        three random numbers between 50 and 256
    """
    return f"rgb({randint(a=50, b=256)},{randint(a=50, b=256)},{randint(a=50, b=256)})"


def build_and_save_indicators_figure(
    fluctuations: Fluctuations, indicators_lines: list[IndicatorLine], output_path: Path
):
    """Show indicators line on a figure.

    Args:
        fluctuations: market data
        indicators_lines: technical indicator lines to be plotted
        output_path: path to save figure
    """

    fig = make_subplots(rows=3, cols=1)

    # plot the candlesticks
    fig.add_trace(
        go.Candlestick(
            x=fluctuations.get_series("open_time"),
            open=fluctuations.get_series("open"),
            high=fluctuations.get_series("high"),
            low=fluctuations.get_series("low"),
            close=fluctuations.get_series("close"),
        ),
        row=1,
        col=1,
    )
    fig.update_yaxes(fixedrange=False)

    # overlay indicators lines
    for indicator_line in indicators_lines:
        fig.add_trace(
            go.Scatter(
                name=indicator_line.name,
                x=fluctuations.get_series("open_time"),
                y=pd.Series(indicator_line.values),
                mode="lines",
                marker=dict(color=_generate_random_rgb()),
            ),
            row=1,
            col=1,
        )

    fig.write_html(output_path.as_posix())
