from binance.client import Client
from apicultor.constants import BINANCE_KEY, BINANCE_SECRET


class BinanceClient:
    """Main interface between binance and athena."""

    def __init__(self):
        self.client = Client(BINANCE_KEY, BINANCE_SECRET)
