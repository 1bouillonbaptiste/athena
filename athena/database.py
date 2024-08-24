from athena.types import Candle
import pandas as pd
from pathlib import Path


class Database:
    def __init__(self, fluctuations: pd.DataFrame):
        self.fluctuations = fluctuations

    @classmethod
    def from_candles(cls, candles: list[Candle]):
        """Convert candles to a single dataframe."""
        fluctuations = (
            pd.concat([pd.DataFrame(candle.to_dict(), index=[0]) for candle in candles])
            .sort_values(by="open_time", ascending=True)
            .drop_duplicates(subset="open_time")
            .reset_index(drop=True)
            .astype({"open_time": "datetime64[ns]", "close_time": "datetime64[ns]"})
        )
        return cls(fluctuations)

    @classmethod
    def from_directory(cls, path: Path):
        """Load .csv files from directory and merge them into one dataframe."""
        fluctuations = (
            pd.concat([pd.read_csv(file) for file in path.glob("*.csv")])
            .sort_values(by="open_time", ascending=True)
            .drop_duplicates(subset=["open_time", "coin", "currency", "period"])
            .reset_index(drop=True)
            .astype({"open_time": "datetime64[ns]", "close_time": "datetime64[ns]"})
        )

        unique_coins = fluctuations["coin"].unique()
        if len(unique_coins) > 1:
            raise ValueError(f"Multiple coins detected: {', '.join(unique_coins)}")
        unique_currencies = fluctuations["currency"].unique()
        if len(unique_currencies) > 1:
            raise ValueError(
                f"Multiple currencies detected: {', '.join(unique_currencies)}"
            )
        unique_periods = fluctuations["period"].unique()
        if len(unique_periods) > 1:
            raise ValueError(f"Multiple periods detected: {', '.join(unique_periods)}")

        return cls(fluctuations)
