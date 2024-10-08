from pathlib import Path

import click

from athena.core.config import DataConfig, IndicatorsConfig
from athena.core.context import ProjectContext
from athena.core.interfaces import DatasetLayout, Fluctuations
from athena.entrypoints.utils import load_config
from athena.tradingtools.indicators.build import build_indicator_lines
from athena.tradingtools.indicators.chart import build_and_save_indicators_figure


@click.command()
@click.option(
    "--data-config-path",
    "-dc",
    required=True,
    type=Path,
    help="Path to the data configuration file.",
)
@click.option(
    "--indicators-config-path",
    "-ic",
    required=True,
    type=Path,
    help="Path to the strategy configuration file.",
)
@click.option(
    "--output-path",
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
def visualize(
    data_config_path: Path,
    indicators_config_path: Path,
    output_path: Path,
    root_dir: Path,
):
    """Plot indicators on market data and save the resulting chart.

    Args:
        data_config_path: path to data configuration
        indicators_config_path: path to indicators configuration,
        output_path: directory to save the performance results
        root_dir: raw market data location
    """

    output_path.parent.mkdir(exist_ok=True, parents=True)
    data_config = DataConfig.model_validate(load_config(data_config_path))
    indicators_config = IndicatorsConfig.model_validate(
        load_config(indicators_config_path)
    )

    fluctuations = Fluctuations.load_from_dataset(
        dataset=DatasetLayout(root_dir=root_dir or ProjectContext().raw_data_directory),
        coin=data_config.coin,
        currency=data_config.currency,
        target_period=data_config.period,
        from_date=data_config.from_date,
        to_date=data_config.to_date,
    )

    indicators_lines = build_indicator_lines(
        config=indicators_config, fluctuations=fluctuations
    )

    build_and_save_indicators_figure(
        fluctuations=fluctuations,
        indicators_lines=indicators_lines,
        output_path=output_path,
    )
