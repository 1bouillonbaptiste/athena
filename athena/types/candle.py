import datetime
import pandas as pd
from pydantic import BaseModel, model_validator


class Candle(BaseModel):
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

    coin: str
    currency: str
    period: str
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

    @classmethod
    def from_fluctuation(cls, row: pd.Series):
        """Temporary, wait for collection of candles class."""
        return cls.model_validate(**row.to_dict())

    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.model_dump() == other.model_dump()


class Fluctuations(BaseModel):
    """Collection of candles.

    Attributes:
        _candles: list of candles ordered by their open_time attribute.
        period: candles collection time period (e.g. '1d' or '4h')
    """

    _candles: dict[datetime.datetime, Candle]
    period: str

    @classmethod
    def from_candles(cls, candles: list[Candle]):
        return cls.model_validate(
            {
                "_candles": {
                    candle.open_time: candle
                    for candle in sorted(candles, key=lambda candle: candle.open_time)
                },
                "period": candles[0].period,
            }
        )

    @model_validator(mode="after")
    def check_candles_have_same_period(self):
        """Check candles have the same period."""
        periods = set([candle.period for candle in self._candles.values()])
        if len(periods) > 1:
            periods_str = "[" + ", ".join(periods) + "]"
            raise ValueError(
                f"All candles must have the same period, found {periods_str}."
            )

    def get_candle(self, open_time: datetime.datetime) -> Candle:
        return self._candles.get(open_time)
