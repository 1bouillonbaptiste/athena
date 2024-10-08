import pytest

from athena.tradingtools.indicators import build_indicator, TECHNICAL_INDICATORS


def dummy_indicator(x: int, parameter_a: int, parameter_b: int):
    return x + parameter_a + parameter_b


def test_build_indicator():
    with pytest.raises(NotImplementedError):
        build_indicator(
            name="dummy_indicator", parameters={"parameter_a": 5, "parameter_b": 10}
        )

    TECHNICAL_INDICATORS.update({"dummy_indicator": dummy_indicator})

    indicator_function = build_indicator(
        name="dummy_indicator", parameters={"parameter_a": 5, "parameter_b": 10}
    )

    assert indicator_function(10) == 25
