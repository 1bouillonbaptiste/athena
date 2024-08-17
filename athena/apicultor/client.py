from binance.client import Client

from athena.apicultor.constants import BINANCE_KEY, BINANCE_SECRET


class BinanceClient:
    """Main interface between binance and athena."""

    def __init__(self):
        if BINANCE_KEY is None or BINANCE_SECRET is None:
            self._client = None
        else:
            self._client = Client(BINANCE_KEY, BINANCE_SECRET)

    def get_account(self):
        """Get account infos."""
        return self._client.get_account()

    def get_historical_klines(
        self,
        symbol: str,
        interval: str,
        start_str: str,
        end_str: str,
    ):
        """Get historical klines."""
        return self._client.get_historical_klines(
            symbol=symbol, interval=interval, start_str=start_str, end_str=end_str
        )


def get_assets_balances(client: BinanceClient) -> dict[str, float]:
    """Get account assets balance."""
    return {
        elem["asset"]: float(elem["free"])
        for elem in client.get_account()["balances"]
        if float(elem["free"]) > 0
    }


def get_asset_balance(client: BinanceClient, symbol: str) -> float:
    """Get the available amount of an asset."""
    return get_assets_balances(client=client).get(symbol, 0)
