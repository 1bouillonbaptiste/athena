from typing import Literal

UNITS = {
    "m": "minutes",
    "h": "hours",
    "d": "days",
}


class Period:
    """Helper to convert time frame to time unit and value."""

    def __init__(
        self,
        timeframe: str | None = None,
        value: int | None = None,
        unit: str | None = None,
    ):
        (self.timeframe, self.value, self.unit) = fill_missing_attributes(
            timeframe, value, unit
        )
        self.unit_full = UNITS[self.unit]


def fill_missing_attributes(
    timeframe: str | None = None,
    value: int | None = None,
    unit: Literal["m", "h"] | None = None,
):
    """

    Args:
        timeframe: string containing both value and unit information
        value: time unit number
        unit: the time unit of the value

    Returns:
        same attributes with filled Nones

    Raises:
        ValueError: if timeframe is None and one of value / unit is None
    """

    if timeframe is None:
        if value is None or unit is None:
            raise ValueError(
                "`value` and `unit` must be given when `period` is `None`."
            )
        timeframe = str(value) + unit
    else:
        value = int(timeframe[:-1])
        unit = str(timeframe[-1])

    return timeframe, value, unit
