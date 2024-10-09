from pydantic import BaseModel

from athena.tradingtools.metrics.metrics import TradingMetrics, TradingStatistics


class TradingPerformance(BaseModel):
    """All the financial indicators of a strategy.

    Attributes:

        trading_metrics: raw and cold metrics
        trading_statistics: indicators measuring investments health
    """

    trading_metrics: TradingMetrics
    trading_statistics: TradingStatistics
