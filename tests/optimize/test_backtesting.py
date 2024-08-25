import datetime

import pytest

from athena.core.interfaces import Fluctuations, Candle
from athena.optimize import Strategy, Position
from athena.core.types import Signal, Coin, Side
from athena.optimize.backtesting import (
    get_trades_from_strategy_and_fluctuations,
    check_position_exit_signals,
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
    trades, open_position, _ = get_trades_from_strategy_and_fluctuations(
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
    assert open_position is None


def test_get_trades_from_strategy_and_fluctuations_price_reach_tp(fluctuations):
    strategy = StrategyBuyMondaySellFriday(position_size=0.33, take_profit_pct=0.1)
    trades, open_position, _ = get_trades_from_strategy_and_fluctuations(
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
    assert open_position is None


def test_get_trades_from_strategy_and_fluctuations_price_reach_sl(fluctuations):
    strategy = StrategyBuyMondaySellFriday(position_size=0.33, stop_loss_pct=0.1)
    trades, open_position, _ = get_trades_from_strategy_and_fluctuations(
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
    assert open_position is None


def test_get_trades_from_strategy_and_fluctuations_position_not_closed(fluctuations):
    strategy = StrategyMondayDCA(position_size=0.33)
    trades, open_position, _ = get_trades_from_strategy_and_fluctuations(
        strategy=strategy,
        fluctuations=fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
    )
    assert trades == []
    assert open_position.model_dump() == {
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
    }


@pytest.fixture
def open_position():
    return Position.model_validate(
        {
            "strategy_name": "my_strat",
            "coin": Coin.BTC,
            "currency": Coin.USDT,
            "open_date": datetime.datetime(2024, 8, 20),
            "open_price": 100,
            "amount": 0.9,
            "open_fees": 10,
            "initial_investment": 100,
            "stop_loss": 50,
            "take_profit": 150,
            "side": Side.LONG,
        }
    )


@pytest.fixture
def candle():
    return Candle.model_validate(
        {
            "coin": Coin.BTC,
            "currency": Coin.USDT,
            "period": "1h",
            "open_time": datetime.datetime(2024, 8, 25),
            "close_time": datetime.datetime(2024, 8, 26),
            "high_time": datetime.datetime(2024, 8, 25, hour=12),
            "low_time": datetime.datetime(2024, 8, 25, hour=3),
            "open": 130,
            "high": 151,
            "low": 122,
            "close": 130,
            "volume": 100,
            "quote_volume": 140,
            "nb_trades": 100,
            "taker_volume": 50,
            "taker_quote_volume": 70,
        }
    )


def test_check_position_exit_signals_take_profit(open_position, candle):
    close_price, close_date = check_position_exit_signals(
        position=open_position, candle=candle
    )

    # take_profit is reached at high_time, everything went well
    assert close_price == open_position.take_profit
    assert close_date == datetime.datetime(2024, 8, 25, hour=12)


def test_check_position_exit_signals_stop_loss(open_position, candle):
    candle.low_time = None
    candle.high = 140  # below take_profit
    candle.low = 40  # below stop_loss
    close_price, close_date = check_position_exit_signals(
        position=open_position, candle=candle
    )

    # "low_time" not in row, take close_time
    assert close_price == open_position.stop_loss
    assert close_date == datetime.datetime(2024, 8, 26)


def test_check_position_exit_signals_tp_sl_conflict(open_position, candle):
    candle.low = 40  # below stop_loss
    close_price, close_date = check_position_exit_signals(
        position=open_position, candle=candle
    )

    # even if candle ended well, we reached low before high
    assert close_price == open_position.stop_loss
    assert close_date == datetime.datetime(2024, 8, 25, hour=3)


def test_check_position_exit_signals_undefined_winner(open_position, candle):
    candle.high_time = None
    candle.low_time = None
    close_price, close_date = check_position_exit_signals(open_position, candle=candle)

    # we don't know which of low or high came first, so we take close
    assert close_price == 150
    assert close_date == datetime.datetime(2024, 8, 26)
