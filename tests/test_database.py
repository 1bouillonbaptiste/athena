import pandas as pd
from datetime import datetime

from athena.database import Database
from pandas.testing import assert_frame_equal


def test_database_from_candles(sample_candles):
    assert_frame_equal(
        Database.from_candles(candles=sample_candles(timeframe="4h")).fluctuations,
        pd.DataFrame(
            {
                "coin": ["BTC"] * 2,
                "currency": ["USDT"] * 2,
                "period": ["4h"] * 2,
                "open_time": [
                    datetime.fromisoformat("2020-01-01 00:00:00"),
                    datetime.fromisoformat("2020-01-01 04:00:00"),
                ],
                "open": [7195.2, 7225.0],
                "high": [7245.0, 7236.2],
                "low": [7175.4, 7199.1],
                "close": [7225.0, 7209.8],
                "volume": [2833.7, 2061.3],
                "quote_volume": [20445895.8, 14890182.3],
                "nb_trades": [32476, 29991],
                "taker_volume": [
                    1548.8,
                    1049.7,
                ],
                "taker_quote_volume": [11176594.4, 7582850.4],
            }
        ),
    )


def test_database_from_directory():
    pass
