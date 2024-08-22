import pandas as pd

from athena.optimize import Strategy
from athena.types import Signal


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
                    signals.append(Signal.BUY)
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
    # TODO : use StrategyBuyMondaySellFriday() (stopping before friday) and check no trades are returned
    #        check also portfolio expected wealth (should be coins + some currency)
    pass
