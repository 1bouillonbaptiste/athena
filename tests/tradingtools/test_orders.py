import datetime

from athena.core.interfaces import Candle
from athena.core.types import Side, Coin
from athena.tradingtools.orders import Position

import pytest


@pytest.fixture
def position():
    return Position.open(
        strategy_name="my_strategy",
        coin="BTC",
        currency="USDT",
        open_date=datetime.datetime(2024, 8, 20),
        open_price=100,
        money_to_invest=50,
    )


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


def test_open_position(position):
    assert position.initial_investment == 50
    assert position.open_fees == 0.05
    assert position.amount == 0.49950000000000006
    assert position.amount * position.open_price + position.open_fees == 50


def test_close_position(position):
    position.close(close_date=datetime.datetime(2024, 8, 25), close_price=125)
    assert position.close_fees == 125 * position.amount * 0.001
    assert position.total_fees == 125 * position.amount * 0.001 + position.open_fees
    assert (
        pytest.approx(position.total_profit)
        == position.amount * 125 - 50 - position.total_fees
    )
    assert position.trade_duration == datetime.timedelta(days=5)


def test_check_position_exit_signals_take_profit(open_position, candle):
    close_price, close_date = open_position.check_position_exit_signals(candle=candle)

    # take_profit is reached at high_time, everything went well
    assert close_price == open_position.take_profit
    assert close_date == datetime.datetime(2024, 8, 25, hour=12)


def test_check_position_exit_signals_stop_loss(open_position, candle):
    candle.low_time = None
    candle.high = 140  # below take_profit
    candle.low = 40  # below stop_loss
    close_price, close_date = open_position.check_position_exit_signals(candle=candle)

    # "low_time" not in row, take close_time
    assert close_price == open_position.stop_loss
    assert close_date == datetime.datetime(2024, 8, 26)


def test_check_position_exit_signals_tp_sl_conflict(open_position, candle):
    candle.low = 40  # below stop_loss
    close_price, close_date = open_position.check_position_exit_signals(candle=candle)

    # even if candle ended well, we reached low before high
    assert close_price == open_position.stop_loss
    assert close_date == datetime.datetime(2024, 8, 25, hour=3)


def test_check_position_exit_signals_undefined_winner(open_position, candle):
    candle.high_time = None
    candle.low_time = None
    close_price, close_date = open_position.check_position_exit_signals(candle=candle)

    # we don't know which of low or high came first, so we take close
    assert close_price == 150
    assert close_date == datetime.datetime(2024, 8, 26)
