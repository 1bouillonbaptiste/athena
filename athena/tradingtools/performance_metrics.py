import datetime

from athena.tradingtools.orders import Position

import numpy as np


def trades_to_wealth(
    trades: list[Position]
) -> tuple[np.ndarray, list[datetime.datetime]]:
    """Convert trades to wealth values over time.

    Each point of the array represents the portfolio value at a given time.

    Args:
        trades: a list of closed positions

    Returns:
        wealth over time as numpy array
        time values of the wealth
    """
    return np.array([]), []


def max_drawdown(trades: list[Position]) -> float:
    """Calculate the biggest loss of a portofolio during its lifetime.

    A drawdown is the gap between a high and the low before a new highest high.
    The maximum drawdown is the biggest loss the portfolio had during his lifetime.

    Args:
        trades: a list of closed positions

    Returns:
        the max drawdown of the portfolio.
    """
    wealth, time = trades_to_wealth(trades)
    return 0


def cagr(trades: list[Position]) -> float:
    """Calculate the CAGR (annualized average return) of the portfolio.

    Args:
        trades: a list of closed positions

    Returns:
        the expected annualized return.
    """
    wealth, time = trades_to_wealth(trades)
    return 0


def sortino(trades: list[Position]) -> float:
    """

    TODO: check what sortino is

    Args:
        trades:

    Returns:

    """
    return 0


def sharpe(trades: list[Position]) -> float:
    """

    TODO: check what sharpe ratio is

    Args:
        trades:

    Returns:

    """
    return 0


def calmar(trades: list[Position]) -> float:
    """

    TODO: check what calmar ratio is

    Args:
        trades:

    Returns:

    """
    return 0
