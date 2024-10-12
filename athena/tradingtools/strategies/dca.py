from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, ConfigDict

from athena.core.fluctuations import Fluctuations
from athena.core.types import Signal
from athena.tradingtools.strategies.strategy import Strategy


class Weekday(Enum):
    monday = 0
    tuesday = 1
    wednesday = 2
    thursday = 3
    friday = 4
    saturday = 5
    sunday = 6
    every_day = 7


class StrategyDCAModel(BaseModel):
    """Parameters' configuration model."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    weekday: Weekday = Field(default=Weekday.every_day)
    hour: int = Field(ge=0, le=23, default=0)
    minute: int = Field(ge=0, le=59, default=0)

    @field_validator("weekday", mode="before")
    @classmethod
    def parse_weekday(cls, value: Any) -> float:
        return Weekday[value] if isinstance(value, str) else value


class StrategyDCA(Strategy):
    def __init__(
        self,
        config: StrategyDCAModel,
    ):
        super().__init__()
        self.config = config

    def compute_signals(self, fluctuations: Fluctuations) -> list[Signal]:
        """Buy at a given week day, hour and minute (e.g. buy every monday at 12:00)

        Args:
            fluctuations: market data

        Returns:
            strategy buy / sell / wait signals
        """
        signals = []

        for open_time in fluctuations.get_series("open_time"):
            is_weekday = (open_time.weekday() == self.config.weekday.value) or (
                self.config.weekday == Weekday.every_day
            )
            is_hour = open_time.hour == self.config.hour
            is_minute = open_time.minute == self.config.minute
            if is_weekday and is_hour and is_minute:
                signals.append(Signal.BUY)
            else:
                signals.append(Signal.WAIT)
        return signals
