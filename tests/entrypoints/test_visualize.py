import datetime
import json

import pytest
from click.testing import CliRunner

from athena.cli import app
from athena.core.config import DataConfig, IndicatorsConfig
from athena.core.context import ProjectContext
from athena.core.interfaces import DatasetLayout, Fluctuations
from athena.core.types import Coin, Period
from athena.entrypoints.utils import load_config
from athena.entrypoints.visualize import visualize
from athena.tradingtools.indicators import TECHNICAL_INDICATORS
from athena.tradingtools.indicators.chart import build_and_save_indicators_figure


@pytest.fixture
def data_config():
    return {
        "coin": "BTC",
        "currency": "USDT",
        "period": "1h",
        "from_date": "2020-01-01",
        "to_date": "2020-01-02",
    }


@pytest.fixture
def indicators_config():
    return {
        "indicators": [
            {
                "name": "ichimoku",
                "parameters": {
                    "window_a": 10,
                    "window_b": 20,
                    "window_c": 5,
                },
            },
        ],
    }


def test_run_visualize(
    data_config, indicators_config, generate_candles, tmp_path, mocker
):
    data_config_path = tmp_path / "data_config.yaml"
    indicators_config_path = tmp_path / "indicators_config.yaml"
    root_dir = tmp_path / "raw_market_data"
    output_path = tmp_path / "figure.html"

    data_config_path.write_text(json.dumps(data_config))
    indicators_config_path.write_text(json.dumps(indicators_config))

    start_date = datetime.datetime(2020, 1, 1)
    for day_ii in range(2):
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
            "visualize",
            "--data-config-path",
            data_config_path.as_posix(),
            "--indicators-config-path",
            indicators_config_path.as_posix(),
            "--root-dir",
            root_dir.as_posix(),
            "--output-path",
            output_path.as_posix(),
        ],
    )

    assert runner.exit_code == 0

    assert output_path.exists()
