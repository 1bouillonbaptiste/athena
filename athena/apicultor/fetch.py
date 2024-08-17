from datetime import datetime, timedelta

from athena.apicultor.client import BinanceClient
from athena.apicultor.types import Candle, Period


def fetch_historical_data(
    client: BinanceClient,
    coin: str,
    currency: str,
    period: Period,
    start_date: str,
    end_date: str,
) -> list[Candle]:
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
        open_time = datetime.fromtimestamp(bar[0] / 1000.0)
        close_time = datetime.fromtimestamp(bar[6] / 1000.0)
        if close_time - open_time < (
            timedelta(**{period.unit_full: period.value}) - timedelta(seconds=1)
        ):
            continue
        candles.append(
            Candle(
                coin=coin,
                currency=currency,
                period=period,
                open_time=open_time,
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

    return candles
