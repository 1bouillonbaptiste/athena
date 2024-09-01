from athena.apicultor.fetch import download_daily_market_candles
from pathlib import Path
import datetime

import click


@click.group("athena")
def app():
    """Athena main group."""
    ...


@app.command()
@click.option("--coin", required=True, type=str, help="The coin to be fetched.")
@click.option(
    "--currency", required=True, type=str, help="The currency used to trade the coin."
)
@click.option(
    "--from-date", default="2010-01-01", type=str, help="Download data after this date."
)
@click.option(
    "--to-date",
    default=datetime.date.today().strftime("%Y-%m-%d"),
    type=str,
    help="Download data before this date.",
)
@click.option(
    "--timeframe",
    default="1m",
    type=str,
    help="The base timeframe of each candle (e.g. '1m' or '4h').",
)
@click.option(
    "--output-dir",
    "-o",
    default=Path("/data/athena"),
    type=Path,
    help="Directory to save downloaded candles.",
)
def download(
    coin: str,
    currency: str,
    from_date: str,
    to_date: str,
    timeframe: str,
    output_dir: Path,
):
    download_daily_market_candles(
        coin=coin,
        currency=currency,
        from_date=datetime.datetime.strptime(from_date, "%Y-%m-%d"),
        to_date=datetime.datetime.strptime(to_date, "%Y-%m-%d"),
        timeframe=timeframe,
        output_dir=output_dir,
    )


if __name__ == "__main__":
    app()
