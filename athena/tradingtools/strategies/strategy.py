import re
from typing import Iterable

from athena.core.interfaces import Candle, Fluctuations
from athena.core.types import Signal


class Strategy:
    name: str
    position_size: float
    stop_loss_pct: float | None = None
    take_profit_pct: float | None = None

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

    def get_signals(
        self, fluctuations: Fluctuations
    ) -> Iterable[tuple[Candle, Signal]]:
        """Get the strategy signals associated to input fluctuations.

        Args:
            fluctuations: collection of candles

        Yields:
            a mapping of signal for each date as a dictionary

        Raises:
            ValueError: if signals are inconsistent with fluctuations
        """
        signals = self.compute_signals(fluctuations=fluctuations)

        # TODO : check for some decorator to check size of compute_signals() ?
        if len(signals) > len(fluctuations.candles):
            raise ValueError(
                f"The strategy `{self.name}` produced too many signals, expected {len(fluctuations.candles)}, got {len(signals)}"
            )

        # fill signals with WAIT at the beginning
        signals = [Signal.WAIT] * (len(fluctuations.candles) - len(signals)) + signals
        for candle, signal in zip(
            fluctuations.candles,
            signals,
        ):
            yield candle, signal

    def compute_signals(self, fluctuations: Fluctuations) -> list[Signal]:
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
    return re.sub(r"([A-Z]+)", r" \1", string).split()
