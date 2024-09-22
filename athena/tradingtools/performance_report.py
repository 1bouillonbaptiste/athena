import plotly.graph_objects as go
from plotly.subplots import make_subplots

from athena.core.interfaces import Fluctuations
from athena.tradingtools import Position

from athena.tradingtools.performance_metrics import trades_to_wealth


def save_trades_on_fluctuations(
    trades: list[Position], fluctuations: Fluctuations, filename: str
):
    """Draw trades on fluctuations and save them along the wealth curve.

    Trades are drawn as a straight line between open and close times.

    Args:
        trades: list of closed positions
        fluctuations: market data
        filename: output filename
    """

    fig = make_subplots(rows=2, cols=1)

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

    # overlay trades lifetime
    for trade in trades:
        fig.add_shape(
            type="line",
            x0=trade.open_date,
            y0=trade.open_price,
            x1=trade.close_date,
            y1=trade.close_price,
            line=dict(color="black", width=1),
            row=1,
            col=1,
        )

    # show trades open time with a green point
    fig.add_trace(
        go.Scatter(
            name="buy",
            x=[trade.open_date for trade in trades],
            y=[trade.close_price for trade in trades],
            mode="markers",
            marker=dict(color="green"),
        ),
        row=1,
        col=1,
    )

    # add the wealth over time curve to the plot
    wealth, time = trades_to_wealth(
        trades=trades,
        start_time=fluctuations.candles[0].open_time,
        end_time=fluctuations.candles[-1].open_time,
    )
    fig.add_trace(
        go.Scatter(
            name="wealth",
            x=time,
            y=wealth,
            mode="lines",
            line=dict(color="deepskyblue"),
        ),
        row=2,
        col=1,
    )

    fig.update_layout(title="Trades and wealth over time")
    fig.write_html(filename)


def save_trading_metrics(
    trades: list[Position], fluctuations: Fluctuations, filename: str
):
    """Calculate performance metrics from trades and save them as a table.

    Args:
        trades: list of closed positions
        fluctuations: market data
        filename: output filename
    """
    pass
