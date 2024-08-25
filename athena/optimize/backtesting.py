from athena.optimize import Strategy, Trade, Portfolio, Position
from athena.core.types import Coin, Signal
from athena.core.interfaces import Fluctuations, Candle
import datetime


def get_trades_from_strategy_and_fluctuations(
    strategy: Strategy, fluctuations: Fluctuations
) -> tuple[list[Trade], Position | None, Portfolio]:
    """Compute the trades that a strategy would have made given fluctuations.

    Args:
        strategy: the strategy to get entry signals
        fluctuations: collection of candles

    Returns:
        market movement as a list of trades
    """
    traded_coin = Coin.BTC
    currency = Coin.USDT
    open_position = None
    portfolio = Portfolio.model_validate({"assets": {currency: 100}})

    trades = []
    for candle, signal in strategy.get_signals(fluctuations):
        close_price, close_date = check_position_exit_signals(
            position=open_position, candle=candle
        )
        if (
            (close_price is not None)
            & (close_date is not None)
            & (open_position is not None)
        ):
            new_trade = Trade.from_position(
                position=open_position,
                close_date=close_date,
                close_price=close_price,
            )
            trades.append(new_trade)
            open_position = None

        if signal == Signal.BUY and open_position is None:
            open_position = Position.from_money_to_invest(
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
                coin=currency, amount_to_add=-open_position.initial_investment
            )
            portfolio.update_coin_amount(
                coin=traded_coin, amount_to_add=open_position.amount
            )
        elif signal == Signal.SELL and open_position is not None:
            new_trade = Trade.from_position(
                position=open_position,
                close_date=candle.close_time,
                close_price=candle.close,
            )
            trades.append(new_trade)
            open_position = None

            portfolio.update_coin_amount(
                coin=currency,
                amount_to_add=new_trade.initial_investment + new_trade.total_profit,
            )
            portfolio.update_coin_amount(
                coin=traded_coin, amount_to_add=-new_trade.amount
            )

    return trades, open_position, portfolio


def check_position_exit_signals(
    position: Position | None, candle: Candle
) -> tuple[float | None, datetime.datetime | None]:
    """Check if a candle reaches position's take profit or stop loss.

    Args:
        position: any open position
        candle: a market candle

    Returns:
        close_price: the sell price of the position or None if position remains open
        close_date: the close date of the position or None if position remains open
    """
    if position is None:
        return None, None

    price_reach_tp = (
        (position.take_profit < candle.high)
        if position.take_profit is not None
        else False
    )
    price_reach_sl = (
        (position.stop_loss > candle.low) if position.stop_loss is not None else False
    )

    if (
        price_reach_tp and price_reach_sl
    ):  # candle's price range is very wide, check which bound was reached first
        if (candle.high_time is not None) and (candle.low_time is not None):
            if candle.high_time < candle.low_time:  # price reached high before low
                close_price = position.take_profit
                close_date = candle.high_time
            else:  # price reached low before high
                close_price = position.stop_loss
                close_date = candle.low_time
        else:  # we don't have granularity, assume close price is close enough to real sell price
            close_price = candle.close
            close_date = candle.close_time
    elif price_reach_tp:
        close_price = position.take_profit
        close_date = candle.high_time or candle.close_time
    elif price_reach_sl:
        close_price = position.stop_loss
        close_date = candle.low_time or candle.close_time
    else:  # we don't close the position
        close_price = None
        close_date = None

    return close_price, close_date
