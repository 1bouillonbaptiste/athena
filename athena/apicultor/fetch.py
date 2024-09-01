import logging

from athena.core.interfaces import Candle

import datetime
import tempfile
from pathlib import Path


from athena.apicultor.client import BinanceClient
from athena.core.interfaces import Fluctuations, DatasetLayout
from athena.core.types import Coin, Period
from tqdm import tqdm

logger = logging.getLogger(__name__)


def fetch_historical_data(
    client: BinanceClient,
    coin: str,
    currency: str,
    period: Period,
    start_date: str,
    end_date: str,
) -> Fluctuations:
    """Get candles data between two dates.

    bars contain list of OHLCV values (
        Open time,
        Open,
        High,
        Low,
        Close,
        Volume,
        Close time,
        Quote asset volume,
        Number of trades,
        Taker buy base asset volume,
        Taker buy quote asset volume,
        Ignore
    )
    see https://python-binance.readthedocs.io/en/latest/_modules/binance/client.html#Client.get_historical_klines

    Args:
        client: binance client
        coin: coin of the pair (e.g. 'BTC')
        currency: currency of the pair (e.g. 'USDT')
        period: periodicity of the data to fetch (ex '1h' or '30m')
        start_date: lower bound date
        end_date: upper bound date

    Returns:
        fluctuations: aggregated market historical data
    """
    bars = client.get_historical_klines(
        symbol=coin + currency,
        interval=period.timeframe,
        start_str=start_date,
        end_str=end_date,
    )
    candles = []
    for bar in bars:
        open_time = datetime.datetime.fromtimestamp(bar[0] / 1000.0)
        close_time = datetime.datetime.fromtimestamp(bar[6] / 1000.0)

        # check the candle is closed
        if close_time - open_time < (
            period.to_timedelta() - datetime.timedelta(seconds=1)
        ):
            continue

        # check the datetime is valid
        # see https://docs.python.org/3/library/datetime.html#datetime.datetime.fold
        if open_time.fold == 1:
            continue

        candles.append(
            Candle(
                coin=coin,
                currency=currency,
                period=period.timeframe,
                open_time=open_time,
                close_time=open_time + period.to_timedelta(),
                open=float(bar[1]),
                high=float(bar[2]),
                low=float(bar[3]),
                close=float(bar[4]),
                volume=float(bar[5]),
                quote_volume=float(bar[7]),
                nb_trades=int(bar[8]),
                taker_volume=float(bar[9]),
                taker_quote_volume=float(bar[10]),
            )
        )
    return Fluctuations.from_candles(candles)


def download_daily_market_candles(
    coin: str,
    currency: str,
    from_date: str,
    to_date: str,
    timeframe: str,
    output_dir: Path,
):
    """Download market data from coin / currency pair as fluctuations and save them.

    Args:
        coin: the base coin to download
        currency: the quote currency
        from_date: lower bound date to download candles
        to_date: upper bound date to download candles
        timeframe: timeframe of candles to download
        output_dir: directory to save downloaded candles
    """

    client = BinanceClient()
    period = Period(timeframe=timeframe)
    from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d")
    to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        # retrieve data day by day to limit transfer size
        for day_ii in tqdm(range((to_date - from_date).days)):
            fluctuations = fetch_historical_data(
                client=client,
                coin=coin,
                currency=currency,
                period=period,
                start_date=(from_date + datetime.timedelta(days=day_ii)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                end_date=(from_date + datetime.timedelta(days=day_ii + 1)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            )
            fluctuations.save(tmp_dir / f"fluctuations_{day_ii}.csv")
        filename = DatasetLayout(output_dir).get_dataset_filename(
            coin=Coin[coin], currency=Coin[currency], period=period
        )
        Fluctuations.load(tmp_dir).save(filename)
        logger.info(f"Saved fluctuations to {filename.as_posix()}")
