import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

PriceCollection = list[float] | np.ndarray | pd.Series


class IndicatorLine(BaseModel):
    """Model for an indicator output.

    Attributes:
        name: line name
        values: line values
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    values: np.ndarray
