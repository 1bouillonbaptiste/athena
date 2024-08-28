from pathlib import Path

from athena.core.types import Coin, Period


class DatasetLayout:
    """Interface to manage locations of useful files."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir

    def get_dataset_filename(
        self, coin: Coin, currency: Coin, period: Period | None = None
    ) -> Path:
        """Get the path to pair-related market data."""
        dataset_path = self.root_dir / f"{coin.value}_{currency.value}"
        dataset_path = (
            dataset_path / f"fluctuations_{period.timeframe}.csv"
            if period is not None
            else dataset_path
        )
        return dataset_path
