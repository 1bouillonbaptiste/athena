import datetime
import tempfile
from pathlib import Path


from athena.apicultor.client import BinanceClient
from athena.apicultor.fetch import fetch_historical_data
from athena.core.interfaces import Fluctuations, DatasetLayout
from athena.core.types import Coin, Period
from tqdm import tqdm


# TODO : CLI asking for coin / currency / start_date / end_date / period / ...


def download_market_candles(
    coin: Coin,
    currency: Coin,
    from_date: datetime.datetime,
    to_date: datetime.datetime,
    period: Period,
    output_dir: Path,
) -> None:
    """Download market data from coin / currency pair and save it.

    Args:
        coin: the base coin to download
        currency: the quote currency
        from_date: lower bound date to download candles
        to_date: upper bound date to download candles
        period: periodicity of candles to download
        output_dir: directory to save downloaded candles
    """

    client = BinanceClient()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        # retrieve data day by day to limit transfer size
        for day_ii in tqdm(range((to_date - from_date).days)):
            fluctuations = fetch_historical_data(
                client=client,
                coin=coin.value,
                currency=currency.value,
                period=period,
                start_date=(from_date + datetime.timedelta(days=day_ii)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                end_date=(from_date + datetime.timedelta(days=day_ii + 1)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            )
            fluctuations.save(tmp_dir / f"fluctuations_{day_ii}.csv")
        Fluctuations.load(tmp_dir).save(
            DatasetLayout(output_dir).get_dataset_filename(
                coin=coin, currency=currency, period=period
            )
        )
