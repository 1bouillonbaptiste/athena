import datetime
from functools import cached_property
from pydantic import BaseModel, model_validator
from athena.core.interfaces import Candle
from athena.core.types import Coin

import pandas as pd
from pathlib import Path


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
        sorted_candles = sorted(candles, key=lambda candle: candle.open_time)
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
    def load(cls, path: Path):
        """Load fluctuations from disk.

        Args:
            path: load file if file else load all csv files in dir

        Returns:
            merged candles as a single fluctuations instance.
        """
        if path.is_dir():
            df = pd.concat([pd.read_csv(file) for file in path.glob("*.csv")])
        else:
            df = pd.read_csv(path)
        df = (
            df.sort_values(by="open_time", ascending=True)
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
        return cls.from_candles(candles)
