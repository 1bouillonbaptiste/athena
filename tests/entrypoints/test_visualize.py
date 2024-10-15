import datetime
import json

import pytest
from click.testing import CliRunner

from athena.cli import app
from athena.configs import IndicatorsConfig
from athena.core.fluctuations import Fluctuations
from athena.core.dataset_layout import DatasetLayout
from athena.core.types import Coin, Period
from athena.entrypoints.visualize import _build_indicator_lines
from athena.testing.generate import generate_candles


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
                    "window_a": 2,
                    "window_b": 2,
                    "window_c": 2,
                },
            },
        ],
    }


def test_build_indicator_lines(indicators_config):
    indicator_lines = _build_indicator_lines(
        config=IndicatorsConfig.model_validate(indicators_config),
        fluctuations=Fluctuations.from_candles(generate_candles(size=10)),
    )

    assert len(indicator_lines) == 4

    assert [line.name for line in indicator_lines] == [
        "span_a",
        "span_b",
        "base",
        "conversion",
    ]


def test_run_visualize(
    data_config,
    indicators_config,
    tmp_path,
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
