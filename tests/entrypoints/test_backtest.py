import datetime
import json

from click.testing import CliRunner
import pytest

from athena.core.interfaces import Fluctuations, DatasetLayout
from athena.core.types import Coin, Period

from athena.entrypoints.cli import app


@pytest.fixture
def config():
    return {
        "data": {
            "coin": "BTC",
            "currency": "USDT",
            "period": "1h",
            "from_date": "2020-01-01",
            "to_date": "2020-01-03",
        },
        "strategy": {
            "name": "strategy_dca",
            "parameters": {
                "weekday": "every_day",
                "hour": 12,
                "stop_loss_pct": 0.01,
                "take_profit_pct": 0.01,
                "position_size": 0.01,
            },
        },
    }


def test_run_backtest(config, generate_candles, tmp_path):
    config_path = tmp_path / "config.yaml"
    root_dir = tmp_path / "raw_market_data"
    output_dir = tmp_path / "results"

    config_path.write_text(json.dumps(config))

    start_date = datetime.datetime(2020, 1, 1)
    for day_ii in range(3):
        Fluctuations.from_candles(
            generate_candles(
                from_date=start_date + datetime.timedelta(days=day_ii),
                to_date=start_date + datetime.timedelta(days=day_ii + 1),
            )
        ).save(
            DatasetLayout(root_dir).localize_file(
                coin=Coin.BTC,
                currency=Coin.USDT,
                period=Period(timeframe="1m"),
                date=start_date + datetime.timedelta(days=day_ii),
            )
        )

    runner = CliRunner().invoke(
        app,
        [
            "backtest",
            "--config-path",
            config_path.as_posix(),
            "--root-dir",
            root_dir.as_posix(),
            "--output-dir",
            output_dir.as_posix(),
        ],
    )

    assert runner.exit_code == 0

    assert (output_dir / "performance_report.html").exists()
