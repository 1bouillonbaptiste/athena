import datetime
import pytest
import numpy as np

from athena.tradingtools.metrics.metrics import (
    trades_to_wealth,
    calculate_max_drawdown,
    calculate_cagr,
    calculate_sharpe,
    calculate_sortino,
    calculate_calmar,
)


@pytest.mark.parametrize(
    "start_time, end_time, expected_wealth, expected_time",
    [
        (
            None,
            None,
            [0.0983006, 0.0968011, 0.0569169462],
            [
                datetime.datetime(2024, 8, 6),
                datetime.datetime(2024, 9, 6),
                datetime.datetime(2024, 10, 6),
            ],
        ),
        (
            datetime.datetime(2024, 7, 1),
            None,
            [0, 0.0983006, 0.0968011, 0.0569169462],
            [
                datetime.datetime(2024, 7, 1),
                datetime.datetime(2024, 8, 6),
                datetime.datetime(2024, 9, 6),
                datetime.datetime(2024, 10, 6),
            ],
        ),
        (
            None,
            datetime.datetime(2024, 11, 1),
            [0.0983006, 0.0968011, 0.0569169462, 0.0170327923],
            [
                datetime.datetime(2024, 8, 6),
                datetime.datetime(2024, 9, 6),
                datetime.datetime(2024, 10, 6),
                datetime.datetime(2024, 11, 1),
            ],
        ),
        (
            datetime.datetime(2024, 7, 1),
            datetime.datetime(2024, 11, 1),
            [0, 0.0983006, 0.0968011, 0.0569169462, 0.0170327923],
            [
                datetime.datetime(2024, 7, 1),
                datetime.datetime(2024, 8, 6),
                datetime.datetime(2024, 9, 6),
                datetime.datetime(2024, 10, 6),
                datetime.datetime(2024, 11, 1),
            ],
        ),
    ],
)
def test_trades_to_wealth(
    start_time, end_time, expected_wealth, expected_time, sample_trades
):
    wealth, time = trades_to_wealth(
        sample_trades, start_time=start_time, end_time=end_time
    )
    assert np.allclose(wealth, expected_wealth, rtol=1e-3)
    assert time == expected_time


def test_calculate_max_drawdown(sample_trades):
    assert calculate_max_drawdown(trades=sample_trades) == 0.041


def test_calculate_cagr(sample_trades):
    assert calculate_cagr(trades=sample_trades) == 1.358


def test_calculate_shape(sample_trades):
    assert calculate_sharpe(sample_trades) == 0.24


def test_calculate_sortino(sample_trades):
    assert calculate_sortino(sample_trades) == 0.728


def test_calculate_calmar(sample_trades):
    assert calculate_calmar(sample_trades) == pytest.approx(33.1219512195122)
