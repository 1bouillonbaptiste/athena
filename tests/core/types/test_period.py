import pytest

from athena.core.types.period import _fill_missing_attributes


@pytest.mark.parametrize(
    "timeframe, value, unit, expected_values",
    [
        ("4h", None, None, ("4h", 4, "h")),
        ("30m", None, None, ("30m", 30, "m")),
        (None, 1, "h", ("1h", 1, "h")),
    ],
)
def test_fill_missing_attributes(timeframe, value, unit, expected_values):
    assert _fill_missing_attributes(timeframe, value, unit) == expected_values


@pytest.mark.parametrize(
    "timeframe, value, unit",
    [
        (
            None,
            None,
            None,
        ),
        (None, 1, None),
        (None, None, "h"),
    ],
)
def test_fill_missing_attributes_fail(timeframe, value, unit):
    with pytest.raises(ValueError):
        _fill_missing_attributes(timeframe, value, unit)
