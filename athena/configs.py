import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

from athena.core.types import Coin, Period


class DataConfig(BaseModel):
    """Model for dataset creation configuration.

    Attributes:
        coin: the coin to be traded
        currency: the quote asset to trade the coin
        period: the timeframe of the candles data
        from_date: the lower bound date of the dataset.
        to_date: the upper bound date of the dataset.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    coin: Coin
    currency: Coin
    period: Period
    from_date: datetime.datetime | None = None
    to_date: datetime.datetime | None = None

    @field_validator("coin", mode="before")
    @classmethod
    def parse_coin(cls, value: Any) -> Coin:
        return Coin[value] if isinstance(value, str) else value

    @field_validator("currency", mode="before")
    @classmethod
    def parse_currency(cls, value: Any) -> Coin:
        return Coin[value] if isinstance(value, str) else value

    @field_validator("period", mode="before")
    @classmethod
    def parse_period(cls, value: Any) -> Period:
        return Period(timeframe=value) if isinstance(value, str) else value

    @field_validator("from_date", mode="before")
    @classmethod
    def parse_from_date(cls, value: Any) -> datetime.datetime:
        return (
            datetime.datetime.fromisoformat(value) if isinstance(value, str) else value
        )

    @field_validator("to_date", mode="before")
    @classmethod
    def parse_to_date(cls, value: Any) -> datetime.datetime:
        return (
            datetime.datetime.fromisoformat(value) if isinstance(value, str) else value
        )


class IndicatorConfig(BaseModel):
    """Model that stores technical indicator parameters.

    Attributes:
        name: the name of the indicator
        parameters: the parameters of the indicator
    """

    name: str
    parameters: dict[str, Any]


class IndicatorsConfig(BaseModel):
    """Model that stores technical indicator configs."""

    indicators: list[IndicatorConfig]


class StrategyConfig(BaseModel):
    """Model to instantiate a strategy and trading parameters.

    Attributes:
        name: the name of the strategy to evaluate
        parameters: strategy parameters
    """

    name: str
    parameters: dict[str, Any]
