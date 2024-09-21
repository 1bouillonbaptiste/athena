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
            [9.83, -0.15, -3.988],
            [
                datetime.datetime(2024, 8, 21),
                datetime.datetime(2024, 8, 23),
                datetime.datetime(2024, 8, 25),
            ],
        ),
        (
            datetime.datetime(2024, 8, 15),
            None,
            [0, 9.83, -0.15, -3.988],
            [
                datetime.datetime(2024, 8, 15),
                datetime.datetime(2024, 8, 21),
                datetime.datetime(2024, 8, 23),
                datetime.datetime(2024, 8, 25),
            ],
        ),
        (
            None,
            datetime.datetime(2024, 8, 30),
            [9.83, -0.15, -3.988, -3.988],
            [
                datetime.datetime(2024, 8, 21),
                datetime.datetime(2024, 8, 23),
                datetime.datetime(2024, 8, 25),
                datetime.datetime(2024, 8, 30),
            ],
        ),
        (
            datetime.datetime(2024, 8, 15),
            datetime.datetime(2024, 8, 30),
            [0, 9.83, -0.15, -3.988, -3.988],
            [
                datetime.datetime(2024, 8, 15),
                datetime.datetime(2024, 8, 21),
                datetime.datetime(2024, 8, 23),
                datetime.datetime(2024, 8, 25),
                datetime.datetime(2024, 8, 30),
            ],
        ),
    ],
)
def test_trades_to_wealth(start_time, end_time, expected_wealth, expected_time, trades):
    wealth, time = trades_to_wealth(trades, start_time=start_time, end_time=end_time)
    assert np.allclose(wealth, expected_wealth, rtol=1e-3)
    assert time == expected_time


def test_get_max_drawdown(trades):
    # the wealth goes from 9.83 to -3.988
    assert get_max_drawdown(trades) == pytest.approx(13.818, abs=1e-3)


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
