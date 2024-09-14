import datetime

from athena.core.interfaces import Fluctuations
from athena.tradingtools import Strategy
from athena.core.types import Signal, Coin, Side
from athena.tradingtools.backtesting import (
    get_trades_from_strategy_and_fluctuations,
)


class StrategyBuyMondaySellFriday(Strategy):
    def compute_signals(self, fluctuations: Fluctuations) -> list[Signal]:
        """Return dummy signals."""
        signals = []
        for candle in fluctuations.candles:
            match candle.open_time.isoweekday():
                case 6 | 7:  # weekend
                    signals.append(Signal.WAIT)
                case 1:  # all-in on monday, typical crypto player
                    signals.append(Signal.BUY)
                case 2 | 3 | 4:  # no money left
                    signals.append(Signal.WAIT)
                case 5:  # panic sell on friday, typical crypto player
                    signals.append(Signal.SELL)
        return signals


class StrategyMondayDCA(Strategy):
    def compute_signals(self, fluctuations: Fluctuations) -> list[Signal]:
        """Return dummy signals."""
        signals = []
        for candle in fluctuations.candles:
            match candle.open_time.isoweekday():
                case 1:  # dca on monday
                    signals.append(Signal.BUY)
                case _:
                    signals.append(Signal.WAIT)
        return signals


def test_get_trades_from_strategy_and_fluctuations_with_sell_signal(fluctuations):
    strategy = StrategyBuyMondaySellFriday(position_size=0.33)
    trades, _ = get_trades_from_strategy_and_fluctuations(
        strategy=strategy,
        fluctuations=fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
    )

    assert len(trades) == 1
    assert trades[0].model_dump() == {
        "strategy_name": "strategy_buy_monday_sell_friday",
        "coin": Coin.BTC,
        "currency": Coin.USDT,
        "open_date": datetime.datetime.fromisoformat(
            "2024-08-20 00:00:00"
        ),  # open next day = tuesday
        "close_date": datetime.datetime.fromisoformat(
            "2024-08-24 00:00:00"
        ),  # close next day = saturday
        "trade_duration": datetime.timedelta(days=4),
        "initial_investment": 33.0,
        "open_price": 100.0,
        "close_price": 300.0,
        "amount": 0.32966999999999996,
        "stop_loss": None,
        "take_profit": None,
        "open_fees": 0.033,
        "close_fees": 0.09890099999999999,
        "total_fees": 0.131901,
        "total_profit": 65.76909899999998,
        "is_win": True,
        "side": Side.LONG,
    }


def test_get_trades_from_strategy_and_fluctuations_price_reach_tp(fluctuations):
    strategy = StrategyBuyMondaySellFriday(position_size=0.33, take_profit_pct=0.1)
    trades, _ = get_trades_from_strategy_and_fluctuations(
        strategy=strategy,
        fluctuations=fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
    )

    assert len(trades) == 1
    assert trades[0].model_dump() == {
        "strategy_name": "strategy_buy_monday_sell_friday",
        "coin": Coin.BTC,
        "currency": Coin.USDT,
        "open_date": datetime.datetime.fromisoformat(
            "2024-08-20 00:00:00"
        ),  # open next day = tuesday
        "close_date": datetime.datetime.fromisoformat(
            "2024-08-21 00:00:00"  # "high_time" is missing, so we take close_time
        ),  # close next day = saturday
        "trade_duration": datetime.timedelta(days=1),
        "initial_investment": 33.0,
        "open_price": 100.0,
        "close_price": 110.00000000000001,
        "amount": 0.32966999999999996,
        "stop_loss": None,
        "take_profit": 110.00000000000001,
        "open_fees": 0.033,
        "close_fees": 0.0362637,
        "total_fees": 0.06926370000000001,
        "total_profit": 3.1944363,
        "is_win": True,
        "side": Side.LONG,
    }


def test_get_trades_from_strategy_and_fluctuations_price_reach_sl(fluctuations):
    strategy = StrategyBuyMondaySellFriday(position_size=0.33, stop_loss_pct=0.1)
    trades, _ = get_trades_from_strategy_and_fluctuations(
        strategy=strategy,
        fluctuations=fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
    )

    assert len(trades) == 1
    assert trades[0].model_dump() == {
        "strategy_name": "strategy_buy_monday_sell_friday",
        "coin": Coin.BTC,
        "currency": Coin.USDT,
        "open_date": datetime.datetime.fromisoformat(
            "2024-08-20 00:00:00"
        ),  # open next day = tuesday
        "close_date": datetime.datetime.fromisoformat(
            "2024-08-24 00:00:00"
        ),  # close next day = saturday
        "trade_duration": datetime.timedelta(days=4),
        "initial_investment": 33.0,
        "open_price": 100.0,
        "close_price": 300.0,
        "amount": 0.32966999999999996,
        "stop_loss": 90.0,
        "take_profit": None,
        "open_fees": 0.033,
        "close_fees": 0.09890099999999999,
        "total_fees": 0.131901,
        "total_profit": 65.76909899999998,
        "is_win": True,
        "side": Side.LONG,
    }


def test_get_trades_from_strategy_and_fluctuations_position_not_closed(fluctuations):
    strategy = StrategyMondayDCA(position_size=0.33)
    trades, _ = get_trades_from_strategy_and_fluctuations(
        strategy=strategy,
        fluctuations=fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
    )
    assert len(trades) == 1
    assert not trades[0].is_closed
    assert trades[0].model_dump() == {
        "strategy_name": "strategy_monday_dca",
        "coin": Coin.BTC,
        "currency": Coin.USDT,
        "open_date": datetime.datetime.fromisoformat(
            "2024-08-20 00:00:00"
        ),  # open next day = tuesday
        "initial_investment": 33.0,
        "open_price": 100.0,
        "open_fees": 0.033,
        "amount": 0.32966999999999996,
        "side": Side.LONG,
        "stop_loss": None,
        "take_profit": None,
        "close_date": None,
        "close_fees": None,
        "close_price": None,
        "is_win": None,
        "total_fees": None,
        "total_profit": None,
        "trade_duration": None,
    }
