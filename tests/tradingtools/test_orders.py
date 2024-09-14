import datetime

from athena.tradingtools.orders import Position, Trade

import pytest


@pytest.fixture
def position():
    return Position.from_money_to_invest(
        strategy_name="my_strategy",
        coin="BTC",
        currency="USDT",
        open_date=datetime.datetime(2024, 8, 20),
        open_price=100,
        money_to_invest=50,
    )


def test_position_from_money_to_invest(position):
    assert position.initial_investment == 50
    assert position.open_fees == 0.05
    assert position.amount == 0.49950000000000006
    assert position.amount * position.open_price + position.open_fees == 50


def test_trade_from_position(position):
    new_trade = Trade.from_position(
        position, close_date=datetime.datetime(2024, 8, 25), close_price=125
    )
    assert new_trade.close_fees == 125 * position.amount * 0.001
    assert new_trade.total_fees == 125 * position.amount * 0.001 + position.open_fees
    assert (
        pytest.approx(new_trade.total_profit)
        == position.amount * 125 - 50 - new_trade.total_fees
    )
    assert new_trade.trade_duration == datetime.timedelta(days=5)
