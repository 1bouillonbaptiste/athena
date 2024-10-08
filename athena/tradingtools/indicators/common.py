import numpy as np
from pydantic import BaseModel, ConfigDict


class IndicatorLine(BaseModel):
    """Model for an indicator output.

    Attributes:
        name: line name
        values: line values
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    values: np.ndarray
