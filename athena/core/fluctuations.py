import datetime
import logging
from functools import cached_property
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from athena.core.candle import sanitize_candles, load_candles_from_file
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
        sanitized_candles = sanitize_candles(candles)
        sorted_candles = sorted(sanitized_candles, key=lambda candle: candle.open_time)
        return cls(
            candles=sorted_candles,
            period=candles[0].period if candles else Period(timeframe="1m"),
            coin=candles[0].coin if candles else Coin.default_coin(),
            currency=candles[0].currency if candles else Coin.default_currency(),
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
            periods_str = (
                "[" + ", ".join([period.timeframe for period in set(periods)]) + "]"
            )
            raise ValueError(
                f"All candles must have the same period, found {periods_str}."
            )

        if len(set(coins)) > 1:
            coins_str = "[" + ", ".join([coin.value for coin in set(coins)]) + "]"
            raise ValueError(f"All candles must have the same coin, found {coins_str}.")

        if len(set(currencies)) > 1:
            currencies_str = (
                "[" + ", ".join([coin.value for coin in set(currencies)]) + "]"
            )
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
