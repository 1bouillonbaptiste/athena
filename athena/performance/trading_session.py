from pydantic import BaseModel, ConfigDict

from athena.core.config import DataConfig
from athena.core.interfaces.fluctuations import Fluctuations
from athena.core.market_entities import Portfolio, Position, Trade, Candle
from athena.core.types import Signal
from athena.tradingtools.strategies.strategy import Strategy


class TradingSession(BaseModel):
    """Manage position, trades and portfolio during a backtest.

    # TODO: the strategy is useful only for position_size and strategy name. Use StrategyConfig instead ?

    Attributes:
        trades: list of closed positions
        position: an open position or None
        portfolio: available assets
        strategy: a trading algorithm
        config: data configuration
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    trades: list[Trade]
    position: Position | None
    portfolio: Portfolio
    strategy: Strategy
    config: DataConfig

    @classmethod
    def from_config_and_strategy(cls, config: DataConfig, strategy: Strategy):
        return cls(
            trades=[],
            position=None,
            portfolio=Portfolio.default(currency=config.currency),
            strategy=strategy,
            config=config,
        )

    def buy_signal(self, candle: Candle):
        """Create a new buy order if the portfolio has enough currency."""

        if self.position is not None:  # we are already positioned
            return

        money_to_invest = (
            self.portfolio.get_available(self.config.currency)
            * self.strategy.position_size
        )
        if self.portfolio.get_available(self.config.currency) > money_to_invest:
            self.position = Position.open(
                strategy_name=self.strategy.name,
                coin=self.config.coin,
                currency=self.config.currency,
                open_date=candle.close_time,
                open_price=candle.close,
                money_to_invest=money_to_invest,
                stop_loss=candle.close * (1 - self.strategy.stop_loss_pct)
                if self.strategy.stop_loss_pct is not None
                else 0,
                take_profit=candle.close * (1 + self.strategy.take_profit_pct)
                if self.strategy.take_profit_pct is not None
                else float("inf"),
            )
            self.portfolio.update_from_position(position=self.position)

    def sell_signal(self, candle: Candle):
        """Create a new sell order to close any opened position."""
        if self.position is not None:
            trade = self.position.close(
                close_date=candle.close_time,
                close_price=candle.close,
            )
            self.position = None
            self.trades.append(trade)
            self.portfolio.update_from_trade(trade=trade)

    def check_position_exit_signal(self, candle: Candle):
        """Check if the position needs to be closed."""
        if self.position is None:
            return
        signal = self.position.get_exit_signal(candle=candle)
        if signal is not None:
            close_price, close_date = signal.to_price_date(
                position=self.position, candle=candle
            )
            trade = self.position.close(
                close_date=close_date,
                close_price=close_price,
            )
            self.position = None
            self.trades.append(trade)
            self.portfolio.update_from_trade(trade=trade)

    def get_trades_from_fluctuations(
        self, fluctuations: Fluctuations
    ) -> tuple[list[Position], Portfolio]:
        """Apply the trading strategy on market data and get the trades that would have been made on live trading.

        Args:
            fluctuations: collection of candles, mocks a market

        Returns:
            market movement as a list of trades
        """

        for candle, signal in self.strategy.get_signals(fluctuations):
            self.check_position_exit_signal(candle=candle)
            if signal == Signal.BUY:
                self.buy_signal(candle=candle)
            elif signal == Signal.SELL:
                self.sell_signal(candle=candle)

        return self.trades, self.portfolio
