import re
from typing import Iterable, Any

from athena.core.fluctuations import Fluctuations
from athena.core.market_entities import Candle
from athena.core.types import Signal


class Strategy:
    """Abstract class for trading strategies."""

    name: str

    def __init__(
        self,
    ):
        self.name = "_".join(_split_uppercase_words(self.__class__.__name__)).lower()

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

    def update_config(self, parameters: dict[str:Any]):
        """Update strategy config with new parameters"""
        self.config = self.config.model_copy(update=parameters)


def _split_uppercase_words(string: str) -> list[str]:
    """Split the string from words beginning with a capital letter.

    Examples:
        ThisName -> ["This", "Name"]
        ThisIsIMPORTANT -> ["This", "Is", "IMPORTANT"]

    Args:
        string: input sequence to split

    Returns:
        split sequence
    """
    return re.sub(r"([A-Z]+)", r" \1", string).split()
