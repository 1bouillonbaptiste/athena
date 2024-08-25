from athena.optimize import Strategy, Trade, Portfolio, Position
from athena.core.types import Coin, Period, Signal
import pandas as pd
import datetime


def get_trades_from_strategy_and_fluctuations(
    strategy: Strategy, fluctuations: pd.DataFrame
) -> tuple[list[Trade], Position | None, Portfolio]:
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

    period = Period(timeframe=fluctuations["period"].values[0])

    trades = []
    for open_time, signal in strategy.get_signals(fluctuations):
        df_row = fluctuations.loc[fluctuations["open_time"] == open_time]

        close_price, close_date = check_position_exit_signals(
            position=open_position, row=df_row
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
                open_date=pd.to_datetime(df_row["open_time"].values[0]).to_pydatetime()
                + period.to_timedelta(),
                open_price=df_row["close"],
                money_to_invest=portfolio.get_available(currency)
                * strategy.position_size,
                stop_loss=df_row["close"] * (1 - strategy.stop_loss_pct)
                if strategy.stop_loss_pct is not None
                else None,
                take_profit=df_row["close"] * (1 + strategy.take_profit_pct)
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
                close_date=pd.to_datetime(df_row["open_time"].values[0]).to_pydatetime()
                + period.to_timedelta(),
                close_price=df_row["close"],
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
    position: Position | None, row: pd.DataFrame
) -> tuple[float | None, datetime.datetime | None]:
    """Check if a candle reaches position's take profit or stop loss.

    Args:
        position: any open position
        row: a market candle as a dataframe of size 1

    Returns:
        close_price: the sell price of the position or None if position remains open
        close_date: the close date of the position or None if position remains open
    """
    if position is None:
        return None, None

    period = Period(timeframe=row["period"].values[0])
    price_reach_tp = (
        (position.take_profit < row["high"].item())
        if position.take_profit is not None
        else False
    )
    price_reach_sl = (
        (position.stop_loss > row["low"].item())
        if position.stop_loss is not None
        else False
    )

    if (
        price_reach_tp and price_reach_sl
    ):  # candle's price range is very wide, check which bound was reached first
        if ("high_time" in row) and ("low_time" in row):
            if (
                row["high_time"].values[0] < row["low_time"].values[0]
            ):  # price reached high before low
                close_price = position.take_profit
                close_date = pd.to_datetime(row["high_time"].values[0]).to_pydatetime()
            else:  # price reached low before high
                close_price = position.stop_loss
                close_date = pd.to_datetime(row["low_time"].values[0]).to_pydatetime()
        else:  # we don't have granularity, assume close price is close enough to real sell price
            close_price = row["close"].values[0]
            if "close_time" in row:
                close_date = pd.to_datetime(row["close_time"].values[0]).to_pydatetime()
            else:
                close_date = pd.to_datetime(
                    row["open_time"].values[0]
                ).to_pydatetime() + datetime.timedelta(
                    **{period.unit_full: period.value}
                )
    elif price_reach_tp:
        time_column = "high_time" if "high_time" in row else "close_time"
        close_price = position.take_profit
        close_date = pd.to_datetime(row[time_column].values[0]).to_pydatetime()
    elif price_reach_sl:
        time_column = "low_time" if "low_time" in row else "close_time"
        close_price = position.stop_loss
        close_date = pd.to_datetime(row[time_column].values[0]).to_pydatetime()
    else:  # we don't close the position
        close_price = None
        close_date = None

    return close_price, close_date
