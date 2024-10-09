import datetime

import numpy as np

from athena.core.market_entities import Position, Portfolio
from athena.core.types import Coin


def trades_to_wealth(
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
    initial_money = Portfolio.default().get_available(Coin.default_currency())
    wealth = [trade.total_profit for trade in trades]
    time = [trade.close_date for trade in trades]
    if start_time is not None:
        wealth.insert(0, 0)
        time.insert(0, start_time)
    if end_time is not None:
        wealth.append(wealth[-1] if wealth else 0)
        time.append(end_time)

    return np.cumsum(wealth) / initial_money, time


def max_drawdown(trades: list[Position]) -> float:
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
    wealth, _ = trades_to_wealth(trades)
    drawdown = [np.max(wealth[: ii + 1]) - wealth[ii] for ii in range(1, len(wealth))]
    return np.max(drawdown)


def cagr(trades: list[Position]) -> float:
    """Calculate the CAGR (annualized average return) of the portfolio.

    The CAGR (Compound Annual Growth Rate) is the average annual growth rate of an investment over a specified period,
    assuming the profits are reinvested each year.

    Args:
        trades: a list of closed positions

    Returns:
        the annualized average return
    """
    # TODO: add cagr code
    _, _ = trades_to_wealth(trades)
    return 0


def sharpe(trades: list[Position]) -> float:
    """Calculate the risk-reward of a portfolio.

    The Sharpe ratio measures an investment's return relative to its total risk (volatility),
    calculated as the excess return over the risk-free rate divided by the standard deviation of returns.

    Args:
        trades:

    Returns:
    """
    # TODO: add sharpe code
    _, _ = trades_to_wealth(trades)
    return 0


def sortino(trades: list[Position]) -> float:
    """The Sortino ratio measures an investment's return relative to its downside risk, focusing only on negative
    volatility, rather than total volatility like the Sharpe ratio.

    Args:
        trades:

    Returns:
    """
    # TODO: add sortino code
    _, _ = trades_to_wealth(trades)
    return 0


def calmar(trades: list[Position]) -> float:
    """Calculate the Calmar ratio.

    The Calmar ratio measures an investment's return relative to its maximum drawdown,
    assessing performance by comparing annual returns to the worst peak-to-trough loss.

    Args:
        trades:

    Returns:
    """
    # TODO: add calmar code
    _, _ = trades_to_wealth(trades)
    return 0
