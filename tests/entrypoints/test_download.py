import datetime

import pytest
import numpy as np
from click.testing import CliRunner

from athena.entrypoints.cli import app
from athena.core.types import Period, Coin
from athena.core.interfaces import DatasetLayout, Fluctuations


@pytest.fixture
def generate_bars():
    def _generate_bars(
        size=1000,
        timeframe="1m",
        from_date: datetime.datetime | None = None,
        to_date: datetime.datetime | None = None,
    ):
        period = Period(timeframe=timeframe)

        initial_open_time = (
            from_date
            if from_date is not None
            else datetime.datetime.fromisoformat("2020-01-01 00:00:00")
        )
        last_close_time = (
            to_date
            if to_date is not None
            else initial_open_time + period.to_timedelta() * size
        )

        size = int((last_close_time - initial_open_time) / period.to_timedelta())
        close_price = 1000
        bars = []
        for ii in range(size):
            open_price = close_price
            close_price = open_price * (1 + np.random.normal(scale=0.01))
            high_price = np.max([open_price, close_price]) * (
                1 + np.random.beta(a=2, b=5) / 100
            )
            low_price = np.min([open_price, close_price]) * (
                1 - np.random.beta(a=2, b=5) / 100
            )
            volume = (np.random.beta(a=2, b=2) / 2 + 0.25) * 1000
            buyer_volume = volume * (np.random.beta(a=2, b=2) / 2 + 0.25)
            bars.append(
                [
                    (initial_open_time + ii * period.to_timedelta()).timestamp() * 1000,
                    str(open_price),
                    str(high_price),
                    str(low_price),
                    str(close_price),
                    str(volume),
                    (
                        initial_open_time
                        + (ii + 1) * period.to_timedelta()
                        - datetime.timedelta(milliseconds=90)
                    ).timestamp()
                    * 1000,
                    str((open_price + close_price) / 2 * volume),
                    np.random.randint(low=1000, high=10000),
                    str(buyer_volume),
                    str((open_price + close_price) / 2 * buyer_volume),
                    "0",
                ]
            )
        return bars

    return _generate_bars


def test_download_market_candles(generate_bars, mocker, tmp_path):
    from_date = datetime.datetime(2020, 1, 1)
    to_date = datetime.datetime(2020, 1, 15)
    period = Period(timeframe="4h")

    mocker.patch(
        "athena.apicultor.client.BinanceClient.get_historical_klines",
        return_value=generate_bars(
            from_date=from_date,
            to_date=to_date,
            timeframe=period.timeframe,
        ),
    )

    runner = CliRunner().invoke(
        app,
        [
            "download",
            "--coin",
            "BTC",
            "--currency",
            "USDT",
            "--from-date",
            from_date.strftime("%Y-%m-%d"),
            "--to-date",
            to_date.strftime("%Y-%m-%d"),
            "--output-dir",
            str(tmp_path),
            "--timeframe",
            period.timeframe,
        ],
    )

    assert runner.exit_code == 0

    dataset_layout = DatasetLayout(tmp_path)

    dataset_filename = dataset_layout.localize_file(
        coin=Coin.BTC, currency=Coin.USDT, period=period, date=from_date
    )

    assert dataset_filename.exists()

    # we cannot test each date because the mocker returns a bulk of 15 days
    fluctuations_tmp = Fluctuations.load(dataset_filename.parent)

    assert len(fluctuations_tmp.candles) == 6 * 14  # 6 candles a day * 14 days
    assert fluctuations_tmp.candles[0].open_time == from_date
    assert fluctuations_tmp.candles[-1].close_time == to_date
