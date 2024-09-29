import pytest
import pandas as pd
import datetime

from athena.core.interfaces import Fluctuations
from athena.core.types import Period, Coin
from athena.core.interfaces.dataset_layout import DatasetLayout

from pandas.testing import assert_frame_equal
import numpy as np


def test_fluctuations_from_candles(sample_candles):
    assert Fluctuations.from_candles(
        candles=sample_candles(timeframe="4h")
    ).model_dump() == {
        "candles": [
            {
                "open_time": datetime.datetime(2020, 1, 1, 0, 0),
                "close_time": datetime.datetime(2020, 1, 1, 4, 0),
                "high_time": datetime.datetime(2020, 1, 1, 3, 35),
                "low_time": datetime.datetime(2020, 1, 1, 1, 15),
                "coin": "BTC",
                "currency": "USDT",
                "period": "4h",
                "open": 7195.2,
                "high": 7245.0,
                "low": 7175.4,
                "close": 7225.0,
                "nb_trades": 32476,
                "volume": 2833.7,
                "quote_volume": 20445895.8,
                "taker_quote_volume": 11176594.4,
                "taker_volume": 1548.8,
            },
            {
                "open_time": datetime.datetime(2020, 1, 1, 4, 0),
                "close_time": datetime.datetime(2020, 1, 1, 8, 0),
                "high_time": datetime.datetime(2020, 1, 1, 7, 35),
                "low_time": datetime.datetime(2020, 1, 1, 5, 15),
                "coin": "BTC",
                "currency": "USDT",
                "period": "4h",
                "open": 7225.0,
                "high": 7236.2,
                "low": 7199.1,
                "close": 7209.8,
                "nb_trades": 29991,
                "volume": 2061.3,
                "quote_volume": 14890182.3,
                "taker_quote_volume": 7582850.4,
                "taker_volume": 1049.7,
            },
        ],
        "coin": Coin.BTC,
        "currency": Coin.USDT,
        "period": Period(timeframe="4h").timeframe,
    }


def test_fluctuations_get_candle(sample_candles):
    candles = sample_candles(timeframe="4h")
    assert (
        Fluctuations.from_candles(candles=candles).get_candle(
            open_time=candles[0].open_time
        )
        == candles[0]
    )


def test_fluctuations_fails_on_coins(generate_candles):
    with pytest.raises(ValueError, match="All candles must have the same coin"):
        Fluctuations.from_candles(
            candles=generate_candles(
                coin="BTC", from_date=datetime.datetime(2020, 1, 1), size=5
            )
            + generate_candles(
                coin="ETH", from_date=datetime.datetime(2020, 1, 2), size=5
            )
        )


def test_fluctuations_fails_on_currencies(generate_candles):
    with pytest.raises(ValueError, match="All candles must have the same currency"):
        Fluctuations.from_candles(
            candles=generate_candles(
                currency="USDT", from_date=datetime.datetime(2020, 1, 1), size=5
            )
            + generate_candles(
                currency="EUR", from_date=datetime.datetime(2020, 1, 2), size=5
            )
        )


def test_fluctuations_fails_on_periods(generate_candles):
    with pytest.raises(ValueError, match="All candles must have the same period"):
        Fluctuations.from_candles(
            candles=generate_candles(
                timeframe="1m", from_date=datetime.datetime(2020, 1, 1), size=5
            )
            + generate_candles(
                timeframe="2m", from_date=datetime.datetime(2020, 1, 2), size=5
            )
        )


def test_fluctuations_save_to_file(tmp_path, sample_candles, sample_fluctuations):
    Fluctuations.from_candles(candles=sample_candles()).save(
        tmp_path / "fluctuations.csv"
    )
    assert_frame_equal(
        pd.read_csv(tmp_path / "fluctuations.csv").astype(
            {
                "open_time": "datetime64[ns]",
                "high_time": "datetime64[ns]",
                "low_time": "datetime64[ns]",
                "close_time": "datetime64[ns]",
            }
        ),
        sample_fluctuations(),
    )


def test_load_from_dataset(tmp_path, generate_candles):
    start_date = datetime.datetime(2020, 1, 1)
    for day_ii in range(2):
        Fluctuations.from_candles(
            generate_candles(
                from_date=start_date + datetime.timedelta(days=day_ii),
                to_date=start_date + datetime.timedelta(days=day_ii + 1),
            )
        ).save(
            DatasetLayout(tmp_path).localize_file(
                coin=Coin.BTC,
                currency=Coin.USDT,
                period=Period(timeframe="1m"),
                date=start_date + datetime.timedelta(days=day_ii),
            )
        )
    fluctuations = Fluctuations.load_from_dataset(
        dataset=DatasetLayout(tmp_path),
        coin=Coin.BTC,
        currency=Coin.USDT,
        target_period=Period(timeframe="4h"),
    )
    assert len(fluctuations.candles) == 2 * 6  # 2 days * 6 candles a day


def test_load_fluctuations_get_series(tmp_path, sample_candles, generate_candles):
    from_date = datetime.datetime(2020, 1, 1)
    to_date = datetime.datetime(2020, 1, 1, hour=8)
    candles = generate_candles(timeframe="1m", from_date=from_date, to_date=to_date)

    fluctuations = Fluctuations.from_candles(candles=candles)

    assert np.allclose(
        fluctuations.get_series("open"), np.array([candle.open for candle in candles])
    )

    with pytest.raises(ValueError, match="Trying to access unavailable attribute"):
        fluctuations.get_series("this_attribute_does_not_exist")
