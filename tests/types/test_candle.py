import pytest
import pandas as pd
import datetime

from athena.types import Fluctuations, Period

from pandas.testing import assert_frame_equal


def test_fluctuations_from_candles(sample_candles):
    assert Fluctuations.from_candles(
        candles=sample_candles(timeframe="4h")
    ).model_dump() == {
        "candles_mapping": {
            (datetime.datetime(2020, 1, 1, 0, 0), "BTC", "USDT", "4h"): {
                "close": 7225.0,
                "close_time": datetime.datetime(2020, 1, 1, 4, 0),
                "coin": "BTC",
                "currency": "USDT",
                "high": 7245.0,
                "low": 7175.4,
                "nb_trades": 32476,
                "open": 7195.2,
                "open_time": datetime.datetime(2020, 1, 1, 0, 0),
                "period": "4h",
                "quote_volume": 20445895.8,
                "taker_quote_volume": 11176594.4,
                "taker_volume": 1548.8,
                "volume": 2833.7,
            },
            (datetime.datetime(2020, 1, 1, 4, 0), "BTC", "USDT", "4h"): {
                "close": 7209.8,
                "close_time": datetime.datetime(2020, 1, 1, 8, 0),
                "coin": "BTC",
                "currency": "USDT",
                "high": 7236.2,
                "low": 7199.1,
                "nb_trades": 29991,
                "open": 7225.0,
                "open_time": datetime.datetime(2020, 1, 1, 4, 0),
                "period": "4h",
                "quote_volume": 14890182.3,
                "taker_quote_volume": 7582850.4,
                "taker_volume": 1049.7,
                "volume": 2061.3,
            },
        },
        "coin": "BTC",
        "currency": "USDT",
        "period": Period(timeframe="4h").timeframe,
    }


def test_fluctuations_fails_on_coins(sample_candles):
    with pytest.raises(ValueError, match="All candles must have the same coin"):
        Fluctuations.from_candles(
            candles=sample_candles(coin="BTC") + sample_candles(coin="ETH")
        )


def test_fluctuations_fails_on_currencies(sample_candles):
    with pytest.raises(ValueError, match="All candles must have the same currency"):
        Fluctuations.from_candles(
            candles=sample_candles(currency="USDT") + sample_candles(currency="EUR")
        )


def test_fluctuations_fails_on_periods(sample_candles):
    with pytest.raises(ValueError, match="All candles must have the same period"):
        Fluctuations.from_candles(
            candles=sample_candles(timeframe="4h") + sample_candles(timeframe="1h")
        )


def test_fluctuations_save_to_file(tmp_path, sample_candles, sample_fluctuations):
    Fluctuations.from_candles(candles=sample_candles()).save(
        tmp_path / "fluctuations.csv"
    )
    assert_frame_equal(
        pd.read_csv(tmp_path / "fluctuations.csv").astype(
            {"open_time": "datetime64[ns]", "close_time": "datetime64[ns]"}
        ),
        sample_fluctuations(),
    )


def test_load_fluctuations_from_dir(tmp_path, sample_candles, sample_fluctuations):
    sample_fluctuations().to_csv(tmp_path / "fluctuations.csv", index=False)
    assert (
        Fluctuations.load(tmp_path).model_dump()
        == Fluctuations.from_candles(sample_candles()).model_dump()
    )
