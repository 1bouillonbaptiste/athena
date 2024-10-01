from athena.core.interfaces import Fluctuations
from athena.core.types import Signal
from athena.tradingtools.orders import Portfolio, Position
from athena.tradingtools.strategies.strategy import Strategy
from athena.performance.config import DataConfig


def get_trades_from_strategy_and_fluctuations(
    config: DataConfig, strategy: Strategy, fluctuations: Fluctuations
) -> tuple[list[Position], Portfolio]:
    """Apply the trading strategy on market data and get the trades that would have been made on live trading.

    Args:
        config: data parameters
        strategy: the strategy to apply
        fluctuations: collection of candles, mocks a market

    Returns:
        market movement as a list of trades
    """
    portfolio = Portfolio.default(config.currency)

    position = None
    trades = []  # collection of closed positions
    for candle, signal in strategy.get_signals(fluctuations):
        if position is not None:
            close_price, close_date = position.check_exit_signals(candle=candle)
            if (close_price is not None) and (close_date is not None):
                trade = position.close(
                    close_date=close_date,
                    close_price=close_price,
                )
                trades.append(trade)
                portfolio.update_from_trade(trade=trade)
                position = None

        if signal == Signal.BUY and position is None:
            money_to_invest = (
                portfolio.get_available(config.currency) * strategy.position_size
            )
            if portfolio.get_available(config.currency) < money_to_invest:
                continue
            position = Position.open(
                strategy_name=strategy.name,
                coin=config.coin,
                currency=config.currency,
                open_date=candle.close_time,
                open_price=candle.close,
                money_to_invest=money_to_invest,
                stop_loss=candle.close * (1 - strategy.stop_loss_pct)
                if strategy.stop_loss_pct is not None
                else 0,
                take_profit=candle.close * (1 + strategy.take_profit_pct)
                if strategy.take_profit_pct is not None
                else float("inf"),
            )
            portfolio.update_from_position(position=position)
        elif signal == Signal.SELL and position is not None:
            trade = position.close(
                close_date=candle.close_time,
                close_price=candle.close,
            )
            trades.append(trade)

            portfolio.update_from_trade(trade=trade)

            position = None
    return trades, portfolio
