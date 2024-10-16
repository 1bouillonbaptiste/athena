from athena.configs import TradingSessionConfig
from athena.core.fluctuations import Fluctuations
from athena.core.market_entities import (
    Portfolio,
    Position,
    Candle,
    Trade,
    signal_to_values,
)
from athena.core.types import Signal, Coin
from athena.tradingtools.strategies.strategy import Strategy


class TradingSession:
    """Manage position, trades and portfolio during a backtest.

    Args:
        coin: traded coin
        currency: traded currency
        strategy: strategy to generate signals
        config: session configuration
    """

    def __init__(
        self,
        coin: Coin,
        currency: Coin,
        strategy: Strategy,
        config: TradingSessionConfig,
    ):
        self.coin = coin
        self.currency = currency
        self.strategy = strategy
        self.config = config
        self.portfolio = Portfolio.default(currency=self.currency)
        self.position = None
        self.trades = []

    def _reset_state(self):
        self.portfolio = Portfolio.default(currency=self.currency)
        self.position = None
        self.trades = []

    def _buy_signal(self, candle: Candle):
        """Create a new buy order if the portfolio has enough currency."""

        if self.position is not None:  # we are already positioned
            return

        money_to_invest = (
            self.portfolio.get_available(self.currency) * self.config.position_size
        )
        if self.portfolio.get_available(self.currency) > money_to_invest:
            self.position = Position.open(
                strategy_name=self.strategy.name,
                coin=self.coin,
                currency=self.currency,
                open_date=candle.close_time,
                open_price=candle.close,
                money_to_invest=money_to_invest,
                stop_loss=candle.close * (1 - self.config.stop_loss_pct)
                if self.config.stop_loss_pct is not None
                else 0,
                take_profit=candle.close * (1 + self.config.take_profit_pct)
                if self.config.take_profit_pct is not None
                else float("inf"),
            )
            self.portfolio.update_from_position(position=self.position)

    def _sell_signal(self, candle: Candle):
        """Create a new sell order to close any opened position."""
        if self.position is not None:
            trade = self.position.close(
                close_date=candle.close_time,
                close_price=candle.close,
            )
            self.position = None
            self.trades.append(trade)
            self.portfolio.update_from_trade(trade=trade)

    def _check_position_exit_signal(self, candle: Candle):
        """Check if the position needs to be closed."""
        if self.position is None:
            return
        signal = self.position.get_exit_signal(candle=candle)
        if signal is not None:
            close_price, close_date = signal_to_values(
                signal=signal, position=self.position, candle=candle
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
    ) -> tuple[list[Trade], Portfolio]:
        """Apply the trading strategy on market data and get the trades that would have been made on live trading.

        Args:
            fluctuations: collection of candles, mocks a market

        Returns:
            market movement as a list of trades
        """

        self._reset_state()

        for candle, signal in self.strategy.get_signals(fluctuations):
            self._check_position_exit_signal(candle=candle)
            if signal == Signal.BUY:
                self._buy_signal(candle=candle)
            elif signal == Signal.SELL:
                self._sell_signal(candle=candle)

        return self.trades, self.portfolio
