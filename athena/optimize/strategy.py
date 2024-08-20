import pandas as pd
import datetime
from athena.types import Signal
import re


class Strategy:
    name: str
    position_size: float
    stop_loss_pct: float | None = None
    take_profit_pct: float | None = None

    signals: dict[datetime.datetime, Signal] = {}

    def __init__(
        self,
        name: str = None,
        position_size: float = 1,
        stop_loss_pct: float = None,
        take_profit_pct: float = None,
    ):
        self.name = (
            name
            if name is not None
            else "_".join(split_uppercase_words(self.__class__.__name__)).lower()
        )
        self.position_size = position_size
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.signals = None

    def get_signals(self, fluctuations: pd.DataFrame) -> {datetime.datetime, Signal}:
        """Get the strategy signals associated to input fluctuations.

        Args:
            fluctuations: financial data

        Returns:
            a mapping of signal for each date as a dictionary

        Raises:
            ValueError: if signals are inconsistent with fluctuations
        """
        signals = self.compute_signals(fluctuations=fluctuations)

        if len(signals) > len(fluctuations):
            raise ValueError(
                f"The strategy `{self.name}` produced too many signals, expected {len(fluctuations)}, got {len(signals)}"
            )

        # fill signals with WAIT at the beginning
        signals = [Signal.WAIT] * (len(fluctuations) - len(signals)) + signals
        return {
            date: signal
            for date, signal in zip(
                fluctuations["open_time"],
                signals,
            )
        }

    def compute_signals(self, fluctuations: pd.DataFrame) -> list[Signal]:
        """Compute the signals associated to fluctuations based on a strategy.

        Overwrite this method with your own signals computation function.
        The output signal size must match the input fluctuations size, otherwise WAIT will be added at the beginning.

        Args:
            fluctuations: market data fluctuations

        Returns:
            the signals associated to fluctuations

        Raises:
            NotImplementedError: if the strategy is not implemented.
        """
        raise NotImplementedError


def split_uppercase_words(string: str) -> list[str]:
    return re.findall("[A-Z][^A-Z]*", string)
