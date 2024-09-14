from athena.tradingtools import Strategy, Portfolio, Position
from athena.core.types import Coin, Signal
from athena.core.interfaces import Fluctuations


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
    traded_coin = Coin.BTC
    currency = Coin.USDT
    position = None
    portfolio = Portfolio.model_validate({"assets": {currency: 100}})

    trades = []  # collection of closed positions
    for candle, signal in strategy.get_signals(fluctuations):
        if position is not None:
            close_price, close_date = position.check_position_exit_signals(
                candle=candle
            )
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
                else None,
                take_profit=candle.close * (1 + strategy.take_profit_pct)
                if strategy.take_profit_pct is not None
                else None,
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
