import datetime
from pathlib import Path

from athena.core.types import Coin
from athena.tradingtools.orders import Position, Portfolio
from pydantic import BaseModel
from jinja2 import Environment, PackageLoader, select_autoescape

import numpy as np

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from athena.core.interfaces import Fluctuations


class TradingMetrics(BaseModel):
    """Raw statistics.

    Attributes:
        nb_trades: total number of trades
        nb_wins: number of winning trades
        nb_losses: number of losing trades
        total_return: the return at trading session's end
        best_trade: the return of the best trade
        worst_trade: the return of the worst trade
    """

    nb_trades: int
    nb_wins: int
    nb_losses: int
    total_return: float
    best_trade: float
    worst_trade: float


class TradingStatistics(BaseModel):
    """Financial metrics representing trading performances.

    Attributes:
        max_drawdown: the biggest loss of a portfolio over time
        cagr: average annual growth rate
        sharpe_ratio: investment's return relative to its total risk
        sortino_ratio: investment's return relative to its downside risk
        calmar_ratio: investment's return relative to its maximum drawdown
    """

    max_drawdown: float
    cagr: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float


class TradingPerformance(BaseModel):
    """All the financial indicators of a strategy.

    Attributes:

        trading_metrics: raw and cold metrics
        trading_statistics: indicators measuring investments health
    """

    trading_metrics: TradingMetrics
    trading_statistics: TradingStatistics


def _trades_to_wealth(
    trades: list[Position],
    start_time: datetime.datetime | None = None,
    end_time: datetime.datetime | None = None,
) -> tuple[np.ndarray, list[datetime.datetime]]:
    """Convert trades to wealth values over time.

    Each point of the array represents the portfolio value at a given time.

    Args:
        trades: a list of closed positions
        start_time: the optional starting time of the trading session
        end_time: the optional ending time of the trading session

    Returns:
        wealth as a list of float
        time values of the wealth over time
    """
    wealth = [trade.total_profit for trade in trades]
    time = [trade.close_date for trade in trades]
    if start_time is not None:
        wealth.insert(0, 0)
        time.insert(0, start_time)
    if end_time is not None:
        wealth.append(wealth[-1] if wealth else 0)
        time.append(end_time)

    return wealth, time


def _get_max_drawdown(trades: list[Position]) -> float:
    """Calculate the biggest loss of a portofolio during its lifetime.

    A drawdown is peak-to-trough decline in the value of an investment during a specific period.
    The maximum drawdown is the biggest loss the portfolio had before recovery during his lifetime.

    Args:
        trades: a list of closed positions

    Returns:
        the maximum drawdown
    """
    if len(trades) < 2:
        return 0
    wealth, _ = _trades_to_wealth(trades)
    drawdown = [np.max(wealth[: ii + 1]) - wealth[ii] for ii in range(1, len(wealth))]
    return np.max(drawdown)


def _get_cagr(trades: list[Position]) -> float:
    """Calculate the CAGR (annualized average return) of the portfolio.

    The CAGR (Compound Annual Growth Rate) is the average annual growth rate of an investment over a specified period,
    assuming the profits are reinvested each year.

    Args:
        trades: a list of closed positions

    Returns:
        the annualized average return
    """
    # TODO: add cagr code
    _, _ = _trades_to_wealth(trades)
    return 0


def _get_sharpe(trades: list[Position]) -> float:
    """Calculate the risk-reward of a portfolio.

    The Sharpe ratio measures an investment's return relative to its total risk (volatility),
    calculated as the excess return over the risk-free rate divided by the standard deviation of returns.

    Args:
        trades:

    Returns:
    """
    # TODO: add sharpe code
    _, _ = _trades_to_wealth(trades)
    return 0


def _get_sortino(trades: list[Position]) -> float:
    """The Sortino ratio measures an investment's return relative to its downside risk, focusing only on negative
    volatility, rather than total volatility like the Sharpe ratio.

    Args:
        trades:

    Returns:
    """
    # TODO: add sortino code
    _, _ = _trades_to_wealth(trades)
    return 0


def _get_calmar(trades: list[Position]) -> float:
    """Calculate the Calmar ratio.

    The Calmar ratio measures an investment's return relative to its maximum drawdown,
    assessing performance by comparing annual returns to the worst peak-to-trough loss.

    Args:
        trades:

    Returns:
    """
    # TODO: add calmar code
    _, _ = _trades_to_wealth(trades)
    return 0


def _plot_trades_on_fluctuations(trades: list[Position], fluctuations: Fluctuations):
    """Draw trades on fluctuations and save them along the wealth curve.

    Trades are drawn as a straight line between open and close times.

    Args:
        trades: list of closed positions
        fluctuations: market data

    Returns:
        trades over fluctuations as an HTML graph
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
    wealth, time = _trades_to_wealth(
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
    return fig.to_html(full_html=False, include_plotlyjs="cdn")


def _build_metrics(trades: list[Position]) -> TradingMetrics:
    """Calculate raw metrics."""
    nb_trades = len(trades)
    nb_wins = len([trade for trade in trades if trade.is_win])
    return TradingMetrics(
        nb_trades=len(trades),
        nb_wins=nb_wins,
        nb_losses=nb_trades - nb_wins,
        total_return=round(
            np.sum([trade.total_profit for trade in trades])
            / Portfolio.default().get_available(Coin.default_currency()),
            3,
        ),
        best_trade=np.max([trade.profit_pct for trade in trades]),
        worst_trade=np.min([trade.profit_pct for trade in trades]),
    )


def _build_statistics(trades: list[Position]) -> TradingStatistics:
    """Calculate trading statistics."""
    return TradingStatistics(
        max_drawdown=_get_max_drawdown(trades=trades),
        cagr=_get_cagr(trades=trades),
        sortino_ratio=_get_sortino(trades=trades),
        sharpe_ratio=_get_sharpe(trades=trades),
        calmar_ratio=_get_calmar(trades=trades),
    )


def _performance_table(trading_performance: TradingPerformance):
    """Convert TradingPerformance to an HTML table.

    Each TradingMetrics and TradingStatistics are in a separated table.

    Args:
        trading_performance: trading performance

    Returns:
        performance as HTML table
    """

    headerColor = "grey"
    rowEvenColor = "lightgrey"
    rowOddColor = "white"

    fig = make_subplots(
        rows=2,
        cols=1,
        vertical_spacing=0.03,
        specs=[[{"type": "table"}], [{"type": "table"}]],
    )

    metrics_names = list(trading_performance.trading_metrics.model_dump().keys())
    metrics_values = list(trading_performance.trading_metrics.model_dump().values())

    fig.add_trace(
        go.Table(
            header=dict(
                values=["<b>Indicator</b>", "<b>Value</b>"],
                line_color="darkslategray",
                fill_color=headerColor,
                align=["left", "center"],
                font=dict(color="white", size=12),
            ),
            cells=dict(
                values=[
                    metrics_names,
                    metrics_values,
                ],
                line={"color": "darkslategray"},
                # 2-D list of colors for alternating rows
                fill={
                    "color": [rowOddColor, rowEvenColor] * (len(metrics_values) // 2)
                    + [rowOddColor] * (len(metrics_values) % 2)
                },
                align=["left", "center"],
                font=dict(color="darkslategray", size=11),
            ),
        ),
        row=1,
        col=1,
    )

    statistics_names = list(trading_performance.trading_statistics.model_dump().keys())
    statistics_values = list(
        trading_performance.trading_statistics.model_dump().values()
    )
    fig.add_trace(
        go.Table(
            header=dict(
                values=["<b>Indicator</b>", "<b>Value</b>"],
                line_color="darkslategray",
                fill_color=headerColor,
                align=["left", "center"],
                font=dict(color="white", size=12),
            ),
            cells=dict(
                values=[
                    statistics_names,
                    statistics_values,
                ],
                line={"color": "darkslategray"},
                # 2-D list of colors for alternating rows
                fill={
                    "color": [rowOddColor, rowEvenColor] * (len(metrics_values) // 2)
                    + [rowOddColor] * (len(metrics_values) % 2)
                },
                align=["left", "center"],
                font=dict(color="darkslategray", size=11),
            ),
        ),
        row=1,
        col=1,
    )

    fig.update_layout(title="Trading Performance Indicators")
    return fig.to_html(full_html=False, include_plotlyjs="cdn")


def build_and_save_trading_report(
    trades: list[Position], fluctuations: Fluctuations, output_path: Path
):
    """Create a report from trades and save it to disk.

    Args:
        trades: closed positions
        fluctuations: market data
        output_path: HMTL file location to save the report
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    env = Environment(loader=PackageLoader("athena"), autoescape=select_autoescape())
    template = env.get_template("performance_report.html")
    report = template.render(
        metrics=_performance_table(
            trading_performance=TradingPerformance(
                trading_statistics=_build_statistics(trades),
                trading_metrics=_build_metrics(trades),
            )
        ),
        trades=_plot_trades_on_fluctuations(trades=trades, fluctuations=fluctuations),
    )

    Path(output_path).write_text(report)
