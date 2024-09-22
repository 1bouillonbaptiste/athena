import datetime

from athena.tradingtools.orders import Position

import numpy as np


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
    wealth = [trade.total_profit for trade in trades]
    time = [trade.close_date for trade in trades]
    if start_time is not None:
        wealth.insert(0, 0)
        time.insert(0, start_time)
    if end_time is not None:
        wealth.append(wealth[-1] if wealth else 0)
        time.append(end_time)

    return wealth, time


def get_max_drawdown(trades: list[Position]) -> float:
    """Calculate the biggest loss of a portofolio during its lifetime.

    A drawdown is the gap between a high and the low before a new highest high.
    The maximum drawdown is the biggest loss the portfolio had during his lifetime.

    Args:
        trades: a list of closed positions

    Returns:
        the max drawdown of the portfolio.
    """
    if len(trades) < 2:
        return 0
    wealth, _ = trades_to_wealth(trades)
    drawdown = [np.max(wealth[: ii + 1]) - wealth[ii] for ii in range(1, len(wealth))]
    return np.max(drawdown)


def get_cagr(trades: list[Position]) -> float:
    """Calculate the CAGR (annualized average return) of the portfolio.

    Args:
        trades: a list of closed positions

    Returns:
        the expected annualized return.
    """
    _, _ = trades_to_wealth(trades)
    return 0


def get_sortino(trades: list[Position]) -> float:
    """

    TODO: check what sortino is

    Args:
        trades:

    Returns:

    """
    _, _ = trades_to_wealth(trades)
    return 0


def get_sharpe(trades: list[Position]) -> float:
    """

    TODO: check what sharpe ratio is

    Args:
        trades:

    Returns:

    """
    _, _ = trades_to_wealth(trades)
    return 0


def get_calmar(trades: list[Position]) -> float:
    """

    TODO: check what calmar ratio is

    Args:
        trades:

    Returns:

    """
    _, _ = trades_to_wealth(trades)
    return 0
