import datetime

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
