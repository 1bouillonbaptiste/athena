import datetime
from pathlib import Path

from athena.core.types import Coin, Period


class DatasetLayout:
    """Interface to manage locations of useful files.

    Candles are saved in files by their day
    """

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir

    def get_dataset_path(self, coin: Coin, currency: Coin, period: Period) -> Path:
        """Get the path to pair-related market data."""
        return self.root_dir / f"{coin.value}_{currency.value}_{period.timeframe}"

    def localize_file(
        self, coin: Coin, currency: Coin, period: Period, date: datetime.datetime
    ):
        date_str = date.strftime("%Y-%m-%d")
        return (
            self.get_dataset_path(coin, currency, period)
            / f"fluctuations_{date_str}.csv"
        )
