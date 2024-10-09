import datetime

import numpy as np
import pytest

from athena.core.fluctuations import Fluctuations
from athena.core.market_entities import Position
from athena.performance.report import (
    build_and_save_trading_report,
)
from athena.tradingtools.metrics.metrics import (
    trades_to_wealth,
)


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
    trade1 = Position.open(
        open_date=datetime.datetime(2024, 8, 20),
        open_price=100,
        money_to_invest=50,
    ).close(close_date=datetime.datetime(2024, 8, 21), close_price=120)

    trade2 = Position.open(
        open_date=datetime.datetime(2024, 8, 22),
        open_price=130,
        money_to_invest=50,
    ).close(close_date=datetime.datetime(2024, 8, 23), close_price=130)

    trade3 = Position.open(
        open_date=datetime.datetime(2024, 8, 24),
        open_price=130,
        money_to_invest=50,
    ).close(close_date=datetime.datetime(2024, 8, 25), close_price=120)
    return [trade1, trade2, trade3]


@pytest.mark.parametrize(
    "start_time, end_time, expected_wealth, expected_time",
    [
        (
            None,
            None,
            [0.0983006, 0.0968011, 0.0569169462],
            [
                datetime.datetime(2024, 8, 21),
                datetime.datetime(2024, 8, 23),
                datetime.datetime(2024, 8, 25),
            ],
        ),
        (
            datetime.datetime(2024, 8, 15),
            None,
            [0, 0.0983006, 0.0968011, 0.0569169462],
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
            [0.0983006, 0.0968011, 0.0569169462, 0.0170327923],
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
            [0, 0.0983006, 0.0968011, 0.0569169462, 0.0170327923],
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
def test__trades_to_wealth(
    start_time, end_time, expected_wealth, expected_time, trades
):
    wealth, time = trades_to_wealth(trades, start_time=start_time, end_time=end_time)
    assert np.allclose(wealth, expected_wealth, rtol=1e-3)
    assert time == expected_time


def test_build_and_save_trading_report(trades, generate_candles, tmp_path):
    output_path = tmp_path / "report.pdf"
    build_and_save_trading_report(
        trades=trades,
        fluctuations=Fluctuations.from_candles(
            generate_candles(
                timeframe="4h",
                from_date=datetime.datetime(2024, 8, 18),
                to_date=datetime.datetime(2024, 8, 26),
            )
        ),
        output_path=output_path,
    )
    assert output_path.exists()
