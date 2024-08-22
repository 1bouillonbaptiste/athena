from athena.optimize import Strategy, Trade, Portfolio, Position
from athena.types import Coin
import pandas as pd

from athena.types import Signal


def get_trades_from_strategy_and_fluctuations(
    strategy: Strategy, fluctuations: pd.DataFrame
) -> tuple[list[Trade], Position | None]:
    """Compute the trades that a strategy would have made given fluctuations.

    Args:
        strategy: the strategy to get entry signals
        fluctuations: financial data

    Returns:
        market movement as a list of trades
    """
    traded_coin = Coin.BTC
    currency = Coin.USDT
    open_position = None
    portfolio = Portfolio.model_validate({"assets": {currency: 100}})

    trades = []
    for open_time, signal in strategy.get_signals(fluctuations):
        match signal:
            case Signal.WAIT:
                continue
            case Signal.BUY:
                df_row = fluctuations.loc[fluctuations["open_time"] == open_time]
                if open_position is None:
                    open_position = Position.from_money_to_invest(
                        strategy_name=strategy.name,
                        coin=traded_coin,
                        currency=currency,
                        open_date=pd.to_datetime(
                            df_row["open_time"].values[0]
                        ).to_pydatetime(),
                        open_price=df_row["close"],
                        money_to_invest=portfolio.get_available(currency)
                        * strategy.position_size,
                        stop_loss=df_row["close"] * strategy.stop_loss_pct
                        if strategy.stop_loss_pct is not None
                        else None,
                        take_profit=df_row["close"] * strategy.take_profit_pct
                        if strategy.take_profit_pct is not None
                        else None,
                    )
                continue
            case Signal.SELL:
                # TODO : check if an open position already exists
                #        if yes, close it at close price and create a new trade
                continue
        # TODO : check if a position needs to be closed (price reaches tp, sl, limit date)
        #        if yes, close it at price and create a new trade
    return trades, open_position
