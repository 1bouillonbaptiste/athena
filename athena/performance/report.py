from pathlib import Path

import plotly.graph_objects as go
from jinja2 import Environment, PackageLoader, select_autoescape
from plotly.subplots import make_subplots

from athena.core.fluctuations import Fluctuations
from athena.core.market_entities import Position
from athena.performance.models import (
    TradingMetrics,
    TradingPerformance,
    TradingStatistics,
)
from athena.tradingtools.metrics.metrics import (
    trades_to_wealth,
)


def _plot_trades_on_fluctuations(trades: list[Position], fluctuations: Fluctuations):
    """Draw trades on fluctuations and save them along the wealth curve.

    Trades are drawn as a straight line between open and close times.

    Args:
        trades: list of closed positions
        fluctuations: market data

    Returns:
        trades over fluctuations as an HTML graph
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

    # overlay trades lifetime
    shapes = []
    for trade in trades:
        shapes.extend(
            [
                dict(
                    type="line",
                    x0=trade.open_date,
                    y0=trade.open_price,
                    x1=trade.close_date,
                    y1=trade.open_price,
                    line=dict(color="black", width=1),
                ),
                dict(
                    type="line",
                    x0=trade.close_date,
                    y0=trade.open_price,
                    x1=trade.close_date,
                    y1=trade.close_price,
                    line=dict(
                        color="forestgreen" if trade.is_win else "crimson", width=1
                    ),
                ),
            ]
        )
    fig.update_layout(shapes=shapes)

    # show trades open time with a green point
    fig.add_trace(
        go.Scatter(
            name="buy",
            x=[trade.open_date for trade in trades],
            y=[trade.open_price for trade in trades],
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
        row=3,
        col=1,
    )

    fig.update_layout(
        title="Trades and wealth over time",
        width=1000,
        height=800,
    )
    return fig.to_html(full_html=False, include_plotlyjs="cdn")


def _performance_table(trading_performance: TradingPerformance):
    """Convert TradingPerformance to an HTML table.

    Each TradingMetrics and TradingStatistics are in a separated table.

    Args:
        trading_performance: trading performance

    Returns:
        performance as HTML table
    """

    def _fill_color(
        size: int, even_color: str = "lightgrey", odd_color: str = "white"
    ) -> list[str]:
        """Alternate even and odd colors."""
        return [odd_color, even_color] * (size // 2) + [odd_color] * (size % 2)

    def _build_table(dictionary: dict):
        return go.Table(
            header=dict(
                values=["<b>Indicator</b>", "<b>Value</b>"],
                line_color="darkslategray",
                fill_color=header_color,
                align=["left", "center"],
                font=dict(color="white", size=12),
            ),
            cells=dict(
                values=[
                    list(dictionary.keys()),
                    list(dictionary.values()),
                ],
                line={"color": "darkslategray"},
                # 2-D list of colors for alternating rows
                fill={
                    "color": _fill_color(
                        size=len(dictionary.values()),
                        even_color=row_even_color,
                        odd_color=row_odd_color,
                    )
                },
                align=["left", "center"],
                font=dict(color="darkslategray", size=11),
            ),
        )

    header_color = "grey"
    row_even_color = "lightgrey"
    row_odd_color = "white"

    fig = make_subplots(
        rows=2,
        cols=1,
        vertical_spacing=0.03,
        specs=[[{"type": "table"}], [{"type": "table"}]],
    )

    fig.add_trace(
        _build_table(dictionary=trading_performance.trading_metrics.model_dump()),
        row=1,
        col=1,
    )

    fig.add_trace(
        _build_table(dictionary=trading_performance.trading_statistics.model_dump()),
        row=2,
        col=1,
    )

    fig.update_layout(
        title="Performance Indicators",
        width=400,
    )
    return fig.to_html(full_html=False, include_plotlyjs="cdn")


def build_and_save_trading_report(
    trades: list[Position],
    fluctuations: Fluctuations,
    output_path: Path,
    show_trades: bool = True,
):
    """Create a report from trades and save it to disk.

    Args:
        trades: closed positions
        fluctuations: market data
        output_path: HMTL file location to save the report
        show_trades: plot the trades on candlesticks or not, could be long in case of many trades
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    trades_html = (
        _plot_trades_on_fluctuations(trades=trades, fluctuations=fluctuations)
        if show_trades
        else ""
    )

    env = Environment(loader=PackageLoader("athena"), autoescape=select_autoescape())
    template = env.get_template("performance_report.html")

    report = template.render(
        metrics=_performance_table(
            trading_performance=TradingPerformance(
                trading_statistics=TradingStatistics.from_trades(trades),
                trading_metrics=TradingMetrics.from_trades(trades),
            )
        ),
        trades=trades_html,
    )

    Path(output_path).write_text(report)
