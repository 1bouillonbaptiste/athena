from athena.core.context import ProjectContext
from athena.client.fetch import download_daily_market_candles
from athena.tradingtools.backtesting import backtest as backtest_main, BacktestConfig
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
@click.option(
    "--overwrite",
    default=False,
    is_flag=True,
    help="Remove existing candles if set.",
)
def download(
    coin: str,
    currency: str,
    from_date: str,
    to_date: str,
    timeframe: str,
    output_dir: Path,
    overwrite: bool,
):
    download_daily_market_candles(
        coin=coin.upper(),
        currency=currency.upper(),
        from_date=from_date,
        to_date=to_date,
        timeframe=timeframe,
        output_dir=output_dir,
        overwrite=overwrite,
    )


@app.command()
@click.option(
    "--config-path",
    "-c",
    required=True,
    type=Path,
    help="Path to the backtesting configuration file.",
)
@click.option(
    "--output-dir",
    "-o",
    required=True,
    type=Path,
    help="Directory to save backtesting results.",
)
@click.option(
    "--root-dir",
    "-r",
    default=ProjectContext().raw_data_directory,
    type=Path,
    help="Location of raw market data.",
)
def backtest(
    config_path: Path,
    output_dir: Path,
    root_dir: Path,
):
    backtest_main(
        config=BacktestConfig.model_validate_json(config_path.read_text()),
        output_dir=output_dir,
        root_dir=root_dir,
    )


if __name__ == "__main__":
    app()
