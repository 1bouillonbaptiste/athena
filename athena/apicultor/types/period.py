UNITS = {
    "m": "minutes",
    "h": "hours",
}


class Period:
    """Helper to convert time frame to time unit and value."""

    def __init__(
        self,
        timeframe: str | None = None,
        value: int | None = None,
        unit: str | None = None,
    ):
        if timeframe is None:
            if value is None or unit is None:
                raise ValueError(
                    "`value` and `unit` must be given when `period` is `None`."
                )
            timeframe = str(value) + unit
        else:
            value = int(timeframe[:-1])
            unit = str(timeframe[-1])

        self.timeframe = timeframe
        self.value = value
        self.unit = unit
        self.unit_full = UNITS[unit]
