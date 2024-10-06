import datetime

from dataclasses import dataclass, asdict

import pandas as pd

from athena.core.types import Coin, Period

AVAILABLE_ATTRIBUTES = (
    "open",
    "high",
    "low",
    "close",
    "open_time",
    "high_time",
    "low_time",
    "close_time",
    "volume",
    "quote_volume",
    "nb_trades",
    "taker_volume",
    "taker_quote_volume",
)


@dataclass
class Candle:
    """Indicators of a specific candle.

    coin: the base coin
    currency: the currency used to trade the coin
    period: the time frame of the candle (e.g. '1m' or '4h')
    open_time: candle opening time
    open: opening price of the base coin
    high: highest price reached by the base coin during the candle life
    low: lowest price reached by the base coin during the candle life
    close: last price of the coin during the candle life
    volume: coin's total traded volume
    quote_volume: currency's total traded volume
    nb_trades: number of trades completed in the candle
    taker_volume: the volume of coin from selling orders that have been filled (taker_volume / volume > 0.5 is high demand)
    taker_quote_volume: the volume of currency earned by selling orders that have been filled
    """

    coin: Coin
    currency: Coin
    period: Period
    open_time: datetime.datetime

    close_time: datetime.datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    quote_volume: float
    nb_trades: int
    taker_volume: float
    taker_quote_volume: float

    high_time: datetime.datetime | None = None
    low_time: datetime.datetime | None = None

    def __eq__(self, other):
        return asdict(self) == asdict(other)

    @classmethod
    def is_available_attribute(cls, attr: str) -> bool:
        return attr in AVAILABLE_ATTRIBUTES

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(
            {attribute: str(value) for attribute, value in asdict(self).items()},
            index=[0],
        )
