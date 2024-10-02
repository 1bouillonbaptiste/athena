from pydantic import BaseModel


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
