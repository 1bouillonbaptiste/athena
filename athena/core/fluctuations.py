import datetime
import logging
from functools import cached_property
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from athena.core.market_entities import Candle
from athena.core.dataset_layout import DatasetLayout
from athena.core.types import Coin, Period

logger = logging.getLogger(__name__)


class Fluctuations(BaseModel):
    """Collection of candles.

    Attributes:
        candles: list of candles ordered by their open_time attribute.
        coin: the base coin
        currency: the currency used to trade the coin
        period: candles time period (e.g. '1d' or '4h')
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, use_enum_values=True)

    candles: list[Candle]
    coin: Coin
    currency: Coin
    period: Period

    @field_validator("period", mode="before")
    @classmethod
    def parse_period(cls, value: Any) -> Period:
        return Period(timeframe=value) if isinstance(value, str) else value

    @cached_property
    def candles_mapping(self):
        """Maps a date to a candle's index with the same `open_time`."""
        return {candle.open_time: ii for ii, candle in enumerate(self.candles)}

    def __len__(self):
        return len(self.candles)

    @classmethod
    def from_candles(cls, candles: list[Candle]):
        sanitized_candles = _sanitize_candles(candles)
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

        return self

    def get_candle(self, open_time: datetime.datetime) -> Candle:
        return self.candles[self.candles_mapping.get(open_time)]

    def get_series(self, attribute_name: str) -> pd.Series:
        """Get the time series of attribute `name` from candles."""
        if not Candle.is_available_attribute(attribute_name):
            raise ValueError("Trying to access unavailable attribute.")
        return pd.Series(
            [getattr(candle, attribute_name) for candle in self.candles],
            index=[candle.open_time for candle in self.candles],
        )

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
        df = pd.concat([candle.to_dataframe() for candle in self.candles])
        df.to_csv(path.as_posix(), index=False)

    @classmethod
    def load_from_dataset(
        cls,
        dataset: DatasetLayout,
        coin: Coin,
        currency: Coin,
        target_period: Period = None,
        from_date: datetime.datetime | None = None,
        to_date: datetime.datetime | None = None,
    ):
        """Retrieve candles from a dataset interface.

        Args:
            dataset: dataset layout object
            coin: coin to be loaded
            currency: currency to base the coin
            target_period: target period
            from_date: keep candles after this date, defaults to 1900-01-01
            to_date: keep candles before this date, defaults to today

        Returns:
            merged candles as a single fluctuations instance.
        """
        from_date = from_date or datetime.datetime(1900, 1, 1)
        to_date = to_date or datetime.datetime.today()
        dates = [
            from_date + datetime.timedelta(days=ii)
            for ii in range((to_date - from_date).days + 1)
        ]

        all_candles = []
        for date in dates:
            filename = dataset.localize_file(
                coin=coin, currency=currency, date=date, period=Period(timeframe="1m")
            )
            if filename.is_file():
                all_candles.extend(
                    load_candles_from_file(
                        filename=filename, target_period=target_period
                    )
                )
        return cls.from_candles(all_candles)


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
        candles = _convert_candles_to_period(candles, target_period=target_period)
    return candles


def _merge_candles(candles: list[Candle]) -> Candle:
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


def _convert_candles_to_period(
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
                _merge_candles(sorted_candles[new_candle_start_index : ii + 1])
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


def _sanitize_candles(candles: list[Candle]) -> list[Candle]:
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
