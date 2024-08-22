import pandas as pd

import datetime

from athena.optimize import Strategy
from athena.types import Signal, Coin, Side
from athena.optimize.backtesting import get_trades_from_strategy_and_fluctuations


class StrategyBuyMondaySellFriday(Strategy):
    def compute_signals(self, fluctuations: pd.DataFrame) -> list[Signal]:
        """Return dummy signals."""
        signals = []
        for _, row in fluctuations.iterrows():
            match row["open_time"].isoweekday():
                case 6 | 7:  # weekend
                    signals.append(Signal.WAIT)
                case 1:  # all-in on monday, typical crypto player
                    signals.append(Signal.BUY)
                case 2 | 3 | 4:  # no money left
                    signals.append(Signal.WAIT)
                case 5:  # panic sell on friday, typical crypto player
                    signals.append(Signal.SELL)
        return signals


def test_get_trades_from_strategy_and_fluctuations_with_sell_signal():
    # TODO : use StrategyBuyMondaySellFriday() with sell signal, check the trade == expected_trade
    #        check also portfolio expected wealth
    pass


def test_get_trades_from_strategy_and_fluctuations_price_reach_tp():
    # TODO : use StrategyBuyMondaySellFriday() with price reaching take profit, check the trade == expected_trade
    #        check also portfolio expected wealth
    pass


def test_get_trades_from_strategy_and_fluctuations_price_reach_sl():
    # TODO : use StrategyBuyMondaySellFriday() with price reaching stop loss, check the trade == expected_trade
    #        check also portfolio expected wealth
    pass


def test_get_trades_from_strategy_and_fluctuations_position_not_closed():
    strategy = StrategyBuyMondaySellFriday(position_size=0.33)
    fluctuations = pd.DataFrame(
        {
            "open_time": pd.date_range("2024-08-19", "2024-08-25", freq="D"),
            "close": [100, 150, 200, 250, 300, 350, 400],
        }
    )
    trades, open_position = get_trades_from_strategy_and_fluctuations(
        strategy=strategy, fluctuations=fluctuations
    )
    assert trades == []
    assert open_position.model_dump() == {
        "strategy_name": "strategy_buy_monday_sell_friday",
        "coin": Coin.BTC,
        "currency": Coin.USDT,
        "open_date": datetime.datetime.fromisoformat("2024-08-19 00:00:00"),
        "initial_investment": 33.0,
        "open_price": 100.0,
        "open_fees": 0.033,
        "amount": 0.32966999999999996,
        "side": Side.LONG,
        "stop_loss": None,
        "take_profit": None,
    }
