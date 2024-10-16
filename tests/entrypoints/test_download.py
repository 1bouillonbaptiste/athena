import datetime

from click.testing import CliRunner

from athena.cli import app
from athena.core.fluctuations import Fluctuations
from athena.core.dataset_layout import DatasetLayout
from athena.core.types import Coin, Period
from athena.testing.generate import generate_bars


def test_download_market_candles(mocker, tmp_path):
    from_date = datetime.datetime(2020, 1, 1)
    to_date = datetime.datetime(2020, 1, 2)
    period = Period(timeframe="1m")

    mocker.patch(
        "athena.client.binance.BinanceClient.get_historical_klines",
        return_value=generate_bars(
            from_date=from_date,
            to_date=to_date,
            period=period,
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
    fluctuations_tmp = Fluctuations.load_from_dataset(
        dataset=dataset_layout, coin=Coin.BTC, currency=Coin.USDT, target_period=period
    )

    assert len(fluctuations_tmp.candles) == 60 * 24  # 1 candle each minute * 60m * 24h
    assert fluctuations_tmp.candles[0].open_time == from_date
    assert fluctuations_tmp.candles[-1].close_time == to_date
