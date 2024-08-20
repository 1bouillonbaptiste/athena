import datetime

from athena.optimize.orders import Position, Trade
from athena.types import Side

import pytest


@pytest.fixture
def position():
    return Position(
        strategy_name="my_strategy",
        coin="BTC",
        currency="USDT",
        open_date=datetime.datetime(2024, 8, 20),
        open_price=100,
        amount=0.1,
        stop_loss=50,
        take_profit=150,
        side=Side.LONG,
    )


def test_position(position):
    assert position.model_dump() == {
        "strategy_name": "my_strategy",
        "coin": "BTC",
        "currency": "USDT",
        "open_date": datetime.datetime(2024, 8, 20),
        "open_price": 100,
        "amount": 0.1,
        "stop_loss": 50,
        "take_profit": 150,
        "side": Side.LONG,
    }


def test_trade(position):
    assert Trade.from_position(
        position, close_date=datetime.datetime(2024, 8, 25), close_price=125
    ).model_dump() == {
        "strategy_name": "my_strategy",
        "coin": "BTC",
        "currency": "USDT",
        "open_date": datetime.datetime(2024, 8, 20),
        "close_date": datetime.datetime(2024, 8, 25),
        "open_price": 100,
        "close_price": 125,
        "amount": 0.1,
        "stop_loss": 50,
        "take_profit": 150,
        "side": Side.LONG,
    }
