from athena.core.context import ProjectContext

from athena.tradingtools.backtesting import backtest as backtest_main, BacktestConfig
from pathlib import Path

import click


@click.command()
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
