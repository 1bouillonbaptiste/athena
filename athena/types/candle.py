from datetime import datetime
import pandas as pd


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

    def __init__(
        self,
        coin: str,
        currency: str,
        period: str,
        open_time: datetime,
        close_time: datetime,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: float,
        quote_volume: float,
        nb_trades: int,
        taker_volume: float,
        taker_quote_volume: float,
    ):
        self.coin = coin
        self.currency = currency
        self.period = period
        self.open_time = open_time
        self.close_time = close_time
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.quote_volume = quote_volume
        self.nb_trades = nb_trades
        self.taker_volume = taker_volume
        self.taker_quote_volume = taker_quote_volume

    @classmethod
    def from_fluctuation(cls, row: pd.Series):
        """Temporary, wait for collection of candles class."""
        return cls(**row.to_dict())

    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def to_dict(self):
        return self.__dict__
