import datetime
from typing import Any
from pathlib import Path

from athena.core.context import ProjectContext
from athena.tradingtools import Strategy, Portfolio, Position
from athena.core.types import Coin, Signal, Period
from athena.core.interfaces import Fluctuations, DatasetLayout
from athena.tradingtools.strategies import init_strategy
from athena.tradingtools.performance_report import build_and_save_trading_report

from pydantic import BaseModel, field_validator, ConfigDict


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


class StrategyConfig(BaseModel):
    """Model to instantiate a strategy and trading parameters.

    Attributes:
        name: the name of the strategy to evaluate
        parameters: strategy parameters
    """

    name: str
    parameters: dict[str, Any]


class BacktestConfig(BaseModel):
    """Model for backtesting configuration.

    Attributes:
        data: data configuration
        strategy: strategy configuration
    """

    data: DataConfig
    strategy: StrategyConfig


def get_trades_from_strategy_and_fluctuations(
    strategy: Strategy, fluctuations: Fluctuations
) -> tuple[list[Position], Portfolio]:
    """Apply the trading strategy on market data and get the trades that would have been made on live trading.

    Args:
        strategy: the strategy to apply
        fluctuations: collection of candles, mocks a market

    Returns:
        market movement as a list of trades
    """
    traded_coin = Coin.default_coin()
    currency = Coin.default_currency()
    portfolio = Portfolio.default()

    position = None
    trades = []  # collection of closed positions
    for candle, signal in strategy.get_signals(fluctuations):
        if position is not None:
            close_price, close_date = position.check_exit_signals(candle=candle)
        else:
            close_price = close_date = None
        if (
            (close_price is not None)
            & (close_date is not None)
            & (position is not None)
        ):
            position.close(
                close_date=close_date,
                close_price=close_price,
            )
            trades.append(position)
            portfolio.update_coin_amount(
                coin=currency,
                amount_to_add=position.initial_investment + position.total_profit,
            )
            portfolio.update_coin_amount(
                coin=traded_coin, amount_to_add=-position.amount
            )
            position = None

        if signal == Signal.BUY and position is None:
            position = Position.open(
                strategy_name=strategy.name,
                coin=traded_coin,
                currency=currency,
                open_date=candle.close_time,
                open_price=candle.close,
                money_to_invest=portfolio.get_available(currency)
                * strategy.position_size,
                stop_loss=candle.close * (1 - strategy.stop_loss_pct)
                if strategy.stop_loss_pct is not None
                else 0,
                take_profit=candle.close * (1 + strategy.take_profit_pct)
                if strategy.take_profit_pct is not None
                else float("inf"),
            )
            portfolio.update_coin_amount(
                coin=currency, amount_to_add=-position.initial_investment
            )
            portfolio.update_coin_amount(
                coin=traded_coin, amount_to_add=position.amount
            )
        elif signal == Signal.SELL and position is not None:
            position.close(
                close_date=candle.close_time,
                close_price=candle.close,
            )
            trades.append(position)

            portfolio.update_coin_amount(
                coin=currency,
                amount_to_add=position.initial_investment + position.total_profit,
            )
            portfolio.update_coin_amount(
                coin=traded_coin, amount_to_add=-position.amount
            )

            position = None
    if position is not None:
        trades.append(position)
    return trades, portfolio


def backtest(config: BacktestConfig, output_dir: Path, root_dir: Path | None = None):
    """Run a trading algorithm on a dataset and save its performance results.

    Args:
        config: backtesting configuration
        output_dir: directory to save the performance results
        root_dir: raw market data location
    """
    fluctuations = Fluctuations.load_from_dataset(
        dataset=DatasetLayout(root_dir=root_dir or ProjectContext().raw_data_directory),
        coin=config.data.coin,
        currency=config.data.currency,
        target_period=config.data.period,
        from_date=config.data.from_date,
        to_date=config.data.to_date,
    )
    strategy = init_strategy(
        strategy_name=config.strategy.name, strategy_params=config.strategy.parameters
    )

    trades, _ = get_trades_from_strategy_and_fluctuations(
        strategy=strategy, fluctuations=fluctuations
    )
    build_and_save_trading_report(
        trades=trades,
        fluctuations=fluctuations,
        output_path=output_dir / "performance_report.html",
    )
