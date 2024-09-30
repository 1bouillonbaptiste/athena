from athena.client.binance import BinanceClient, get_asset_balance, get_assets_balances


def test_get_assets_balances(mocker):
    mocker.patch(
        "athena.client.binance.BinanceClient.get_account",
        return_value={
            "balances": [
                {"asset": "BTC", "free": "1.12"},
                {"asset": "ETH", "free": "0.0"},
                {"asset": "USDT", "free": "12.56"},
            ]
        },
    )
    assert get_assets_balances(client=BinanceClient()) == {"BTC": 1.12, "USDT": 12.56}


def test_get_asset_balance(mocker):
    mocker.patch(
        "athena.client.binance.BinanceClient.get_account",
        return_value={
            "balances": [
                {"asset": "BTC", "free": "1.12"},
                {"asset": "ETH", "free": "0.0"},
                {"asset": "USDT", "free": "12.56"},
            ]
        },
    )

    assert get_asset_balance(client=BinanceClient(), symbol="BTC") == 1.12
    assert get_asset_balance(client=BinanceClient(), symbol="USDT") == 12.56

    assert get_asset_balance(client=BinanceClient(), symbol="ETH") == 0.0
    assert get_asset_balance(client=BinanceClient(), symbol="DOGE") == 0
