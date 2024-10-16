import datetime


from athena.core.fluctuations import Fluctuations
from athena.core.types import Period
from athena.performance.report import (
    build_and_save_trading_report,
)
from athena.testing.generate import generate_candles


def test_build_and_save_trading_report(sample_trades, tmp_path):
    output_path = tmp_path / "report.pdf"
    build_and_save_trading_report(
        trades=sample_trades,
        fluctuations=Fluctuations.from_candles(
            generate_candles(
                period=Period(timeframe="4h"),
                from_date=datetime.datetime(2024, 8, 18),
                to_date=datetime.datetime(2024, 8, 26),
            )
        ),
        output_path=output_path,
    )
    assert output_path.exists()
