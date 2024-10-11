import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator, Field

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


class TradingSessionConfig(BaseModel):
    """Parameters to manage market movements during a trading session.

    Stop loss default value (None or 1) mean never sell.
    Other value mean, e.g. stop_loss_pct is 0.2 and open price is 100, sell if price goes under 80.

    Take profit default value (None or inf) mean never sell.
    Other value mean, e.g. take_profit_pct is 0.2 and open price is 100, sell if price goes above 120.
    For now, we sell when price doubles, could be increased to infinity.

    Attributes:
        position_size: available money percentage to gamble when opening a position
        stop_loss_pct: close a position if loss (in percentage) exceeds this value
        take_profit_pct: close a position if profit (in percentage) exceeds this value

    """

    position_size: float = Field(gt=0, lt=1)
    stop_loss_pct: float = Field(gt=0, le=1)
    take_profit_pct: float = Field(gt=0)

    @field_validator("stop_loss_pct", mode="before")
    @classmethod
    def parse_stop_loss_pct(cls, value: Any) -> float:
        return 1 if value is None else value

    @field_validator("take_profit_pct", mode="before")
    @classmethod
    def parse_take_profit_pct(cls, value: Any) -> float:
        return 1 if value is None else value
