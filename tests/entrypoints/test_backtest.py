import datetime
import json

from click.testing import CliRunner
import pytest

from athena.core.interfaces import Fluctuations

from athena.entrypoints.cli import app


@pytest.fixture
def config():
    return {
        "data": {
            "coin": "BTC",
            "currency": "USDT",
            "period": "1h",
            "from_date": "2020-01-01",
            "to_date": "2021-01-01",
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
    Fluctuations.from_candles(
        generate_candles(
            from_date=datetime.datetime(2020, 1, 1),
            to_date=datetime.datetime(2020, 1, 3),
            timeframe="1m",
        )
    ).save(root_dir / "BTC_USDT_1m")

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
