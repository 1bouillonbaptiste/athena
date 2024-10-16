import datetime

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from athena.core.fluctuations import Fluctuations
from athena.core.dataset_layout import DatasetLayout
from athena.core.types import Coin, Period
from athena.testing.equality import assert_candles_equal
from athena.testing.generate import generate_candles


def test_fluctuations_from_candles():
    candles = generate_candles(size=2, period=Period(timeframe="4h"))
    fluctuations = Fluctuations.from_candles(candles=candles)
    for candle, expected in zip(fluctuations.candles, candles):
        assert_candles_equal(candle, expected)

    assert fluctuations.coin == Coin.default_coin().value
    assert fluctuations.currency == Coin.default_currency().value
    assert fluctuations.period == Period(timeframe="4h")


def test_fluctuations_get_candle():
    candles = generate_candles(size=2, period=Period(timeframe="4h"))
    assert_candles_equal(
        Fluctuations.from_candles(candles=candles).get_candle(
            open_time=candles[0].open_time
        ),
        candles[0],
    )


def test_fluctuations_fails_on_coins():
    with pytest.raises(ValueError, match="All candles must have the same coin"):
        Fluctuations.from_candles(
            candles=generate_candles(
                coin=Coin.BTC, from_date=datetime.datetime(2020, 1, 1), size=5
            )
            + generate_candles(
                coin=Coin.ETH, from_date=datetime.datetime(2020, 1, 2), size=5
            )
        )


def test_fluctuations_fails_on_currencies():
    with pytest.raises(ValueError, match="All candles must have the same currency"):
        Fluctuations.from_candles(
            candles=generate_candles(
                currency=Coin.USDT, from_date=datetime.datetime(2020, 1, 1), size=5
            )
            + generate_candles(
                currency=Coin.EUR, from_date=datetime.datetime(2020, 1, 2), size=5
            )
        )


def test_fluctuations_fails_on_periods():
    with pytest.raises(ValueError, match="All candles must have the same period"):
        Fluctuations.from_candles(
            candles=generate_candles(
                period=Period(timeframe="1m"),
                from_date=datetime.datetime(2020, 1, 1),
                size=5,
            )
            + generate_candles(
                period=Period(timeframe="2m"),
                from_date=datetime.datetime(2020, 1, 2),
                size=5,
            )
        )


def test_fluctuations_save_to_file(tmp_path):
    candles = generate_candles(size=10)
    expected_df = (
        pd.concat([candle.to_dataframe() for candle in candles])
        .reset_index(drop=True)
        .astype(
            {
                "open_time": "datetime64[ns]",
                "high_time": "datetime64[ns]",
                "low_time": "datetime64[ns]",
                "close_time": "datetime64[ns]",
            }
        )
    )

    Fluctuations.from_candles(candles=candles).save(tmp_path / "fluctuations.csv")
    assert_frame_equal(
        pd.read_csv(tmp_path / "fluctuations.csv")
        .astype(
            {
                "open_time": "datetime64[ns]",
                "high_time": "datetime64[ns]",
                "low_time": "datetime64[ns]",
                "close_time": "datetime64[ns]",
            }
        )
        .sort_index(axis=1)[expected_df.columns],
        expected_df,
    )


def test_load_from_dataset(tmp_path):
    start_date = datetime.datetime(2020, 1, 1)
    Fluctuations.from_candles(
        generate_candles(
            from_date=start_date,
            to_date=start_date + datetime.timedelta(hours=12),
        )
    ).save(
        DatasetLayout(tmp_path).localize_file(
            coin=Coin.BTC,
            currency=Coin.USDT,
            period=Period(timeframe="1m"),
            date=start_date,
        )
    )
    fluctuations = Fluctuations.load_from_dataset(
        dataset=DatasetLayout(tmp_path),
        coin=Coin.BTC,
        currency=Coin.USDT,
        target_period=Period(timeframe="1h"),
    )
    assert len(fluctuations.candles) == 12


def test_load_fluctuations_get_series(tmp_path):
    from_date = datetime.datetime(2020, 1, 1)
    to_date = datetime.datetime(2020, 1, 1, hour=8)
    candles = generate_candles(
        period=Period(timeframe="1m"), from_date=from_date, to_date=to_date
    )

    fluctuations = Fluctuations.from_candles(candles=candles)

    assert np.allclose(
        fluctuations.get_series("open").to_numpy(),
        np.array([candle.open for candle in candles]),
    )

    with pytest.raises(ValueError, match="Trying to access unavailable attribute"):
        fluctuations.get_series("this_attribute_does_not_exist")
