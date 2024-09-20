from athena.tradingtools.performance_metrics import (
    get_sharpe,
    get_calmar,
    get_sortino,
    get_max_drawdown,
    get_cagr,
    trades_to_wealth,
)
from athena.core.types import Coin
from athena.tradingtools.orders import Position

import pytest
import datetime
import numpy as np


@pytest.fixture
def trades():
    """Returns 3 closed positions.

    trade 1 : sell at higher price, it's a win
    trade 2 : sell at same price, it's a loss due to fees
    trade 3 : sell at lower price, it's a loss

    Overall we should make money

    Returns:
        trades as list of closed positions
    """
    position1 = Position.open(
        strategy_name="my_strategy",
        coin=Coin.default_coin(),
        currency=Coin.default_currency(),
        open_date=datetime.datetime(2024, 8, 20),
        open_price=100,
        money_to_invest=50,
    )
    (position1.close(close_date=datetime.datetime(2024, 8, 21), close_price=120),)

    position2 = Position.open(
        strategy_name="my_strategy",
        coin=Coin.default_coin(),
        currency=Coin.default_currency(),
        open_date=datetime.datetime(2024, 8, 22),
        open_price=130,
        money_to_invest=50,
    )
    position2.close(close_date=datetime.datetime(2024, 8, 23), close_price=130)

    position3 = Position.open(
        strategy_name="my_strategy",
        coin=Coin.default_coin(),
        currency=Coin.default_currency(),
        open_date=datetime.datetime(2024, 8, 24),
        open_price=130,
        money_to_invest=50,
    )
    position3.close(close_date=datetime.datetime(2024, 8, 25), close_price=120)
    return [position1, position2, position3]


@pytest.mark.parametrize(
    "start_time, end_time, expected_wealth, expected_time",
    [
        (
            None,
            None,
            [100, 100, 100],
            [
                datetime.datetime(2024, 8, 20),
                datetime.datetime(2024, 8, 21),
                datetime.datetime(2024, 8, 21),
            ],
        ),
        (
            datetime.datetime(2024, 8, 15),
            None,
            [100, 100, 100, 100],
            [
                datetime.datetime(2024, 8, 15),
                datetime.datetime(2024, 8, 20),
                datetime.datetime(2024, 8, 21),
                datetime.datetime(2024, 8, 21),
            ],
        ),
        (
            None,
            datetime.datetime(2024, 8, 30),
            [100, 100, 100],
            [
                datetime.datetime(2024, 8, 20),
                datetime.datetime(2024, 8, 21),
                datetime.datetime(2024, 8, 21),
                datetime.datetime(2024, 8, 30),
            ],
        ),
        (
            datetime.datetime(2024, 8, 15),
            datetime.datetime(2024, 8, 30),
            [100, 100, 100],
            [
                datetime.datetime(2024, 8, 15),
                datetime.datetime(2024, 8, 20),
                datetime.datetime(2024, 8, 21),
                datetime.datetime(2024, 8, 21),
                datetime.datetime(2024, 8, 30),
            ],
        ),
    ],
)
def test_trades_to_wealth(start_time, end_time, expected_wealth, expected_time, trades):
    wealth, time = trades_to_wealth(trades, start_time=start_time, end_time=end_time)
    assert np.allclose(wealth, expected_wealth)
    assert time == expected_time


def test_get_max_drawdown():
    maw_drawdown = get_max_drawdown([])  # noqa : F841 (unused)
    pass


def test_get_cagr():
    cagr = get_cagr([])  # noqa : F841 (unused)
    pass


def test_get_sharpe():
    sharpe = get_sharpe([])  # noqa : F841 (unused)
    pass


def test_get_calmar():
    calmar = get_calmar([])  # noqa : F841 (unused)
    pass


def test_get_sortino():
    sortino = get_sortino([])  # noqa : F841 (unused)
    pass
