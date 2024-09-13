from enum import Enum

from athena.core.interfaces import Fluctuations
from athena.core.types import Signal
from athena.optimize.strategies.strategy import Strategy


class Weekday(Enum):
    monday = 0
    tuesday = 1
    wednesday = 2
    thursday = 3
    friday = 4
    saturday = 5
    sunday = 6


class StrategyDCA(Strategy):
    def __init__(
        self, weekday: Weekday | str, hour: int = 0, minute: int = 0, **kwargs
    ):
        super().__init__(**kwargs)

        self.weekday = Weekday[weekday] if isinstance(weekday, str) else weekday
        self.hour = hour
        self.minute = minute

    def compute_signals(self, fluctuations: Fluctuations) -> list[Signal]:
        """Buy at a given week day, hour and minute (e.g. buy every monday at 12:00)

        Args:
            fluctuations: market data

        Returns:
            strategy buy / sell / wait signals
        """
        signals = []
        for open_time in fluctuations.get_series("open_time"):
            is_weekday = open_time.weekday() == self.weekday.value
            is_hour = open_time.hour == self.hour
            is_minute = open_time.minute == self.minute
            if is_weekday and is_hour and is_minute:
                signals.append(Signal.BUY)
            else:
                signals.append(Signal.WAIT)
