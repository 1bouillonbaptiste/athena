from athena.database import Database
from pandas.testing import assert_frame_equal
import pytest
import datetime


def test_database_from_candles(sample_candles, sample_fluctuations):
    assert_frame_equal(
        Database.from_candles(candles=sample_candles(timeframe="4h")).fluctuations,
        sample_fluctuations(timeframe="4h"),
    )


def test_database_from_directory(sample_fluctuations, tmp_path):
    fluctuations = sample_fluctuations(timeframe="4h")
    fluctuations.to_csv(tmp_path / "sample_fluctuations.csv", index=False)

    assert_frame_equal(Database.from_directory(tmp_path).fluctuations, fluctuations)

    fluctuations_2 = fluctuations.copy()
    fluctuations_2["open_time"] = fluctuations_2["open_time"] + datetime.timedelta(
        days=1
    )
    fluctuations_2.to_csv(tmp_path / "sample_fluctuations_2.csv", index=False)

    assert len(Database.from_directory(tmp_path).fluctuations) == 4


def test_database_from_directory_fails_with_multiple_timeframes(
    sample_fluctuations, tmp_path
):
    sample_fluctuations(timeframe="4h").to_csv(
        tmp_path / "sample_fluctuations_1.csv", index=False
    )
    sample_fluctuations(timeframe="2h").to_csv(
        tmp_path / "sample_fluctuations_2.csv", index=False
    )

    with pytest.raises(ValueError):
        Database.from_directory(tmp_path)


def test_database_from_directory_fails_with_multiple_coins(
    sample_fluctuations, tmp_path
):
    sample_fluctuations(coin="BTC").to_csv(
        tmp_path / "sample_fluctuations_1.csv", index=False
    )
    sample_fluctuations(coin="ETH").to_csv(
        tmp_path / "sample_fluctuations_2.csv", index=False
    )

    with pytest.raises(ValueError):
        Database.from_directory(tmp_path)


def test_database_from_directory_fails_with_multiple_currencies(
    sample_fluctuations, tmp_path
):
    sample_fluctuations(currency="USDT").to_csv(
        tmp_path / "sample_fluctuations_1.csv", index=False
    )
    sample_fluctuations(currency="EUR").to_csv(
        tmp_path / "sample_fluctuations_2.csv", index=False
    )

    with pytest.raises(ValueError):
        Database.from_directory(tmp_path)
