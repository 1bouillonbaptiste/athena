import pytest

from athena.core.config import IndicatorsConfig
from athena.tradingtools.indicators.build import build_indicator_lines


@pytest.fixture
def config():
    return IndicatorsConfig.model_validate(
        {
            "indicators": [
                {
                    "name": "ichimoku",
                    "parameters": {"window_a": 2, "window_b": 2, "window_c": 2},
                },
            ]
        }
    )


def test_build_indicator_lines(config, input_fluctuations):
    indicator_lines = build_indicator_lines(
        config=config, fluctuations=input_fluctuations
    )

    assert len(indicator_lines) == 4

    assert [line.name for line in indicator_lines] == [
        "span_a",
        "span_b",
        "base",
        "conversion",
    ]
