import datetime
from functools import cached_property

import numpy as np
from pydantic import BaseModel, model_validator
from athena.core.interfaces import Candle
from athena.core.types import Coin, Period

import pandas as pd
from pathlib import Path

import logging

logger = logging.getLogger(__name__)


class Fluctuations(BaseModel):
    """Collection of candles.

    Attributes:
        candles: list of candles ordered by their open_time attribute.
        coin: the base coin
        currency: the currency used to trade the coin
        period: candles time period (e.g. '1d' or '4h')
    """

    candles: list[Candle]
    coin: Coin
    currency: Coin
    period: str  # TODO : fix type `Period` raises pydantic error when create Fluctuation schema

    @cached_property
    def candles_mapping(self):
        """Maps a date to a candle's index with the same `open_time`."""
        return {candle.open_time: ii for ii, candle in enumerate(self.candles)}

    @classmethod
    def from_candles(cls, candles: list[Candle]):
        sanitized_candles = sanitize_candles(candles)
        sorted_candles = sorted(sanitized_candles, key=lambda candle: candle.open_time)
        return cls(
            candles=sorted_candles,
            period=candles[0].period if candles else "1m",
            coin=candles[0].coin if candles else Coin.BTC,
            currency=candles[0].currency if candles else Coin.USDT,
        )

    @model_validator(mode="after")
    def check_candles_period_coin_currency_unicity(self):
        """Check candles have the same period."""
        if not self.candles:
            return
        periods, coins, currencies = list(
            zip(
                *[
                    (candle.period, candle.coin, candle.currency)
                    for candle in self.candles
                ]
            )
        )

        if len(set(periods)) > 1:
            periods_str = "[" + ", ".join(set(periods)) + "]"
            raise ValueError(
                f"All candles must have the same period, found {periods_str}."
            )

        if len(set(coins)) > 1:
            coins_str = "[" + ", ".join(set(coins)) + "]"
            raise ValueError(f"All candles must have the same coin, found {coins_str}.")

        if len(set(currencies)) > 1:
            currencies_str = "[" + ", ".join(set(currencies)) + "]"
            raise ValueError(
                f"All candles must have the same currency, found {currencies_str}."
            )

        # check candle's list size equals unique indexes size
        if len(self.candles) != len(set(self.candles_mapping.values())):
            raise ValueError("Inconsistent candles mapping.")

    def get_candle(self, open_time: datetime.datetime) -> Candle:
        return self.candles[self.candles_mapping.get(open_time)]

    def get_series(self, attribute_name: str) -> np.ndarray:
        """Get the time series of attribute `name` from candles."""
        if not Candle.is_available_attribute(attribute_name):
            raise ValueError("Trying to access unavailable attribute.")
        return np.array([getattr(candle, attribute_name) for candle in self.candles])

    def save(self, path: Path) -> None:
        """Save fluctuations to disk.

        Fluctuations are saved as a pandas dataframe where each row is a candle.
        We don't need to save the period for now as it can be inferred from candles.
        A future improvement is to create a local sql database to store candles.

        Args:
            path: csv file to dump fluctuations
        """
        if path.is_dir():
            path = path / "fluctuations.csv"

        if not self.candles:  # don't save anything
            return

        path.parent.mkdir(parents=True, exist_ok=True)
        df = pd.concat(
            [pd.DataFrame(candle.model_dump(), index=[0]) for candle in self.candles]
        )
        df.to_csv(path.as_posix(), index=False)

    @classmethod
    def load(cls, path: Path, target_period: Period = None):
        """Load fluctuations from disk.

        Args:
            path: load file if file else load all csv files in dir
            target_period: target period

        Returns:
            merged candles as a single fluctuations instance.
        """
        all_candles = []
        filenames = list(path.glob("*.csv")) if path.is_dir() else [path]
        for filename in filenames:
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
            candles = [Candle.model_validate(row.to_dict()) for _, row in df.iterrows()]

            if target_period is not None:
                candles = convert_candles_to_period(
                    candles, target_period=target_period
                )

            all_candles.extend(candles)
        # remove duplicated candles based on their `open_time`
        all_candles = list(
            {candle.open_time: candle for candle in all_candles}.values()
        )
        return cls.from_candles(all_candles)


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

    src_period = Period(timeframe=candles[0].period)

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
        logger.warning("Last candle could not be closed, won't be kept.")
    return new_candles


def sanitize_candles(candles: list[Candle]) -> list[Candle]:
    """Remove candles that have a volume of 0, no trading activity.

    We want a list of only avaible candles.
    We iterate over the candles list, we remove every candle that has a volume of 0.

    TODO: improve this function to check over prices / highs / lows / closes

    Args:
        candles: list of unsanitized candles

    Returns:
        list of only existing candles
    """
    return [candle for candle in candles if candle.volume > 0]
