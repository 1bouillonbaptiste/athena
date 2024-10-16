import datetime
import logging
from dataclasses import dataclass, asdict
from pathlib import Path

import pandas as pd

from athena.core.types import Period, Coin

logger = logging.getLogger()

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

    def __post_init__(self):
        if isinstance(self.coin, str):
            self.coin = Coin[self.coin]
        if isinstance(self.currency, str):
            self.currency = Coin[self.currency]

        if isinstance(self.period, str):
            self.period = Period(timeframe=self.period)

        if isinstance(self.open_time, pd.Timestamp):
            self.open_time = self.open_time.to_pydatetime()
        if isinstance(self.close_time, pd.Timestamp):
            self.close_time = self.close_time.to_pydatetime()

        if pd.isna(self.high_time):
            self.high_time = None
        if pd.isna(self.low_time):
            self.low_time = None

        if isinstance(self.high_time, pd.Timestamp):
            self.high_time = self.high_time.to_pydatetime()
        if isinstance(self.low_time, pd.Timestamp):
            self.low_time = self.low_time.to_pydatetime()

    def __eq__(self, other):
        return asdict(self) == asdict(other)

    @classmethod
    def is_available_attribute(cls, attr: str) -> bool:
        return attr in AVAILABLE_ATTRIBUTES

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "coin": self.coin.value,
                "currency": self.currency.value,
                "period": self.period.timeframe,
                "open_time": self.open_time,
                "close_time": self.close_time,
                "open": self.open,
                "high": self.high,
                "low": self.low,
                "close": self.close,
                "volume": self.volume,
                "quote_volume": self.quote_volume,
                "nb_trades": self.nb_trades,
                "taker_volume": self.taker_volume,
                "taker_quote_volume": self.taker_quote_volume,
                "high_time": self.high_time,
                "low_time": self.low_time,
            },
            index=[0],
        )


def merge_candles(candles: list[Candle]) -> Candle:
    """Generate a new candle aggregating input candles information.

    This function assumes every candle have the same coin, currency and period.

    Args:
        candles: a list containing candles to be merged

    Returns:
        a new candle aggregating input candles information.

    Raises:
        ValueError: if the input list is empty
    """
    if not candles:
        raise ValueError("Empty candles list.")
    open_candle = min(candles, key=lambda candle: candle.open_time)
    close_candle = max(candles, key=lambda candle: candle.close_time)
    highest_candle = max(candles, key=lambda candle: candle.high)
    lowest_candle = min(candles, key=lambda candle: candle.low)
    return Candle(
        coin=candles[0].coin,
        currency=candles[0].currency,
        period=candles[0].period,
        open_time=open_candle.open_time,
        high_time=highest_candle.open_time,
        low_time=lowest_candle.open_time,
        close_time=close_candle.close_time,
        open=open_candle.open,
        high=highest_candle.high,
        low=lowest_candle.low,
        close=close_candle.close,
        volume=sum([candle.volume for candle in candles]),
        quote_volume=sum([candle.quote_volume for candle in candles]),
        nb_trades=sum([candle.nb_trades for candle in candles]),
        taker_volume=sum([candle.taker_volume for candle in candles]),
        taker_quote_volume=sum([candle.taker_quote_volume for candle in candles]),
    )


def convert_candles_to_period(
    candles: list[Candle], target_period: Period
) -> list[Candle]:
    """Merge close candles into 'bigger' ones.

    We iterate over sorted candles until we reach a theoretical `close_time`.
    Merge candles between last generated candle and current time into a new candle.

    This function assumes every candle have the same coin, currency and period.

    Args:
        candles: list of unsorted candles
        target_period: period of every new candle

    Returns:
        candles whose attributes are computed from input candles.

    Raises:
        ValueError: if an input candle period is lower than target period (e.g. convert "4h" to "1h" is impossible)
    """

    if not candles:
        return []

    src_period = candles[0].period

    if src_period.to_timedelta() > target_period.to_timedelta():
        raise ValueError("Cannot convert candles to lower timeframe.")

    if src_period.to_timedelta() == target_period.to_timedelta():
        return candles

    sorted_candles = sorted(candles, key=lambda candle: candle.open_time)
    new_candles = []
    new_candle_start_index = 0
    new_candle_from_date = sorted_candles[new_candle_start_index].open_time

    for ii in range(len(sorted_candles)):
        theoretical_close_time_is_reached = sorted_candles[ii].close_time >= (
            new_candle_from_date + target_period.to_timedelta()
        )
        if theoretical_close_time_is_reached:
            new_candles.append(
                merge_candles(sorted_candles[new_candle_start_index : ii + 1])
            )
            if ii < (len(sorted_candles) - 1):
                new_candle_start_index = ii + 1
                new_candle_from_date = sorted_candles[new_candle_start_index].open_time
            else:
                # we have reached the end of the loop, don't initiate a new candle
                pass
    if new_candle_start_index != (len(sorted_candles) - 1):
        logger.debug("Last candle could not be closed, won't be kept.")
    return new_candles


def sanitize_candles(candles: list[Candle]) -> list[Candle]:
    """Remove invalid candles.

    Invalid candles are :
        - duplicated candles
        - candles with volume of 0.

    # TODO: improve this function to check over prices / highs / lows / closes

    Args:
        candles: list of raw candles

    Returns:
        filtered candles as a list
    """
    # remove duplicated candles based on their `open_time`
    sanitized_candles = list({candle.open_time: candle for candle in candles}.values())
    sanitized_candles = [candle for candle in sanitized_candles if candle.volume > 0]
    return sanitized_candles


def load_candles_from_file(
    filename: Path, target_period: Period = None
) -> list[Candle]:
    """Build new candles from file data.

    Args:
        filename: path to file containing candles infos
        target_period: aggregate candles to this period

    Returns:
        new candles as a list of candle
    """
    df = (
        pd.read_csv(filename)
        .sort_values(by="open_time", ascending=True)
        .drop_duplicates(subset=["open_time", "coin", "currency", "period"])
        .reset_index(drop=True)
        .astype(
            {
                "open_time": "datetime64[ns]",
                "high_time": "datetime64[ns]",
                "low_time": "datetime64[ns]",
                "close_time": "datetime64[ns]",
            }
        )
    )
    candles = [Candle(**row.to_dict()) for _, row in df.iterrows()]
    if target_period is not None:
        candles = convert_candles_to_period(candles, target_period=target_period)
    return candles
