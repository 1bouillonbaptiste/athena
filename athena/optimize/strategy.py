import pandas as pd
import datetime
from athena.types import Signal


class Strategy:
    signals: dict[datetime.datetime, Signal] = {}

    def __init__(self, fluctuation: pd.DataFrame):
        self.signals = {
            date: signal
            for date, signal in zip(
                fluctuation["open_time"], self.compute_signals(fluctuations=fluctuation)
            )
        }

    def compute_signals(self, fluctuations: pd.DataFrame) -> list[Signal]:
        """Compute the signals associated to fluctuations based on a strategy.

        Overwrite this method with your own signals computation function.

        Args:
            fluctuations: market data fluctuations

        Returns:
            the signals associated to fluctuations

        Raises:
            NotImplementedError: if the strategy is not implemented.
        """
        raise NotImplementedError
