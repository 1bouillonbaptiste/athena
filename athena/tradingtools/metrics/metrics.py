from dataclasses import dataclass, asdict
import datetime

import numpy as np

from athena.core.market_entities import Portfolio, Trade
from athena.core.types import Coin


RISK_FREE_RATE = 0.01


@dataclass
class TradingMetrics:
    """Raw statistics.

    Attributes:
        nb_trades: total number of trades
        nb_wins: number of winning trades
        nb_losses: number of losing trades
        total_return: the return at trading session's end
        best_trade_return: the return of the best trade
        worst_trade_return: the return of the worst trade
    """

    nb_trades: int
    nb_wins: int
    nb_losses: int
    total_return: float
    best_trade_return: float
    worst_trade_return: float

    def model_dump(self):
        return asdict(self)

    @classmethod
    def from_trades(cls, trades: list[Trade]):
        nb_trades = len(trades)
        nb_wins = len([trade for trade in trades if trade.is_win])
        return cls(
            nb_trades=len(trades),
            nb_wins=nb_wins,
            nb_losses=nb_trades - nb_wins,
            total_return=round(
                np.sum([trade.total_profit for trade in trades])
                / Portfolio.default().get_available(Coin.default_currency()),
                3,
            ),
            best_trade_return=round(np.max([trade.profit_pct for trade in trades]), 5),
            worst_trade_return=round(np.min([trade.profit_pct for trade in trades]), 5),
        )


@dataclass
class TradingStatistics:
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

    def model_dump(self):
        return asdict(self)

    @classmethod
    def from_trades(cls, trades: list[Trade]):
        return cls(
            max_drawdown=calculate_max_drawdown(trades=trades),
            cagr=calculate_cagr(trades=trades),
            sortino_ratio=calculate_sortino(trades=trades),
            sharpe_ratio=calculate_sharpe(trades=trades),
            calmar_ratio=calculate_calmar(trades=trades),
        )


def trades_to_wealth(
    trades: list[Trade],
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


def calculate_max_drawdown(trades: list[Trade]) -> float:
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
    return round(float(np.max(drawdown)), 3)


def calculate_cagr(trades: list[Trade]) -> float:
    """Calculate the CAGR (annualized average return) of the portfolio.

    The CAGR (Compound Annual Growth Rate) is the average annual growth rate of an investment over a specified period,
    assuming the profits are reinvested each year.

    Args:
        trades: a list of closed positions

    Returns:
        the annualized average return
    """
    initial_money = Portfolio.default().get_available(Coin.default_currency())
    total_profit = np.sum([trade.total_profit for trade in trades])
    session_years = (trades[-1].close_date - trades[0].open_date).days / 365.0
    if session_years == 0:
        return 0

    cagr = float(
        np.pow((initial_money + total_profit) / initial_money, 1 / session_years)
    )
    return round(cagr, 3)


def calculate_sharpe(trades: list[Trade]) -> float:
    """Calculate the risk-reward of a portfolio.

    The Sharpe ratio measures an investment's return relative to its total risk (volatility),
    calculated as the excess return over the risk-free rate divided by the standard deviation of returns.

    Args:
        trades:

    Returns:
    """
    trades_return = [trade.total_profit / trade.initial_investment for trade in trades]
    returns_avg = np.mean(trades_return)
    returns_std = np.std(trades_return)
    if returns_std == 0:
        return 0

    sharpe = float((returns_avg - RISK_FREE_RATE) / returns_std)
    return round(sharpe, 3)


def calculate_sortino(trades: list[Trade]) -> float:
    """The Sortino ratio measures an investment's return relative to its downside risk, focusing only on negative
    volatility, rather than total volatility like the Sharpe ratio.

    Args:
        trades:

    Returns:
    """
    trades_return = [trade.total_profit / trade.initial_investment for trade in trades]
    returns_avg = np.mean(trades_return)
    returns_negative_std = np.std([ret for ret in trades_return if ret < 0])

    if returns_negative_std == 0:
        return 0

    sharpe = float((returns_avg - RISK_FREE_RATE) / returns_negative_std)
    return round(sharpe, 3)


def calculate_calmar(trades: list[Trade]) -> float:
    """Calculate the Calmar ratio.

    The Calmar ratio measures an investment's return relative to its maximum drawdown,
    assessing performance by comparing annual returns to the worst peak-to-trough loss.

    Args:
        trades:

    Returns:
    """
    max_drawdown = calculate_max_drawdown(trades)
    if max_drawdown == 0:
        return 0
    return calculate_cagr(trades) / calculate_max_drawdown(trades)
