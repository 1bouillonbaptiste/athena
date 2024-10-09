from collections.abc import Iterable
from pathlib import Path
from random import randint
from typing import Callable

import click
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from athena.configs import DataConfig, IndicatorsConfig
from athena.settings import Settings
from athena.core.fluctuations import Fluctuations
from athena.core.dataset_layout import DatasetLayout
from athena.entrypoints.utils import load_config
from athena.tradingtools.indicators import build_indicator
from athena.tradingtools.indicators.common import IndicatorLine


def _generate_random_rgb():
    """Create a color from random numbers.

    The color value starts at 50 to be light enough.

    Returns:
        three random numbers between 0 and 200
    """
    min_color = 0
    max_color = 200

    def _random_number():
        return randint(a=min_color, b=max_color)

    return f"rgb({_random_number()},{_random_number()},{_random_number()})"


def _build_and_save_indicators_figure(
    fluctuations: Fluctuations, indicators_lines: list[IndicatorLine], output_path: Path
):
    """Show indicators line on a figure.

    Args:
        fluctuations: market data
        indicators_lines: technical indicator lines to be plotted
        output_path: path to save figure
    """

    fig = make_subplots(rows=1, cols=1)

    # plot the candlesticks
    fig.add_trace(
        go.Candlestick(
            x=fluctuations.get_series("open_time"),
            open=fluctuations.get_series("open"),
            high=fluctuations.get_series("high"),
            low=fluctuations.get_series("low"),
            close=fluctuations.get_series("close"),
        ),
        row=1,
        col=1,
    )
    fig.update_yaxes(fixedrange=False)

    # overlay indicators lines
    for indicator_line in indicators_lines:
        fig.add_trace(
            go.Scatter(
                name=indicator_line.name,
                x=fluctuations.get_series("open_time"),
                y=pd.Series(indicator_line.values),
                mode="lines",
                marker=dict(color=_generate_random_rgb()),
            ),
            row=1,
            col=1,
        )

    fig.update_layout(
        title="Augmented fluctuations",
        width=1500,
        height=1500,
    )

    fig.write_html(output_path.as_posix())


def _build_indicator_lines(
    config: IndicatorsConfig, fluctuations: Fluctuations
) -> list[Callable]:
    """Build indicators lines from a configuration.

    Args:
        config: indicators configuration.
        fluctuations: market data

    Returns:
        indicator lines as a list
    """
    indicators_lines = []
    for indicator_config in config.indicators:
        indicator_function = build_indicator(
            name=indicator_config.name, parameters=indicator_config.parameters
        )
        new_indicators_lines = indicator_function(fluctuations)
        if isinstance(new_indicators_lines, Iterable):
            indicators_lines.extend(new_indicators_lines)
        else:
            indicators_lines.append(new_indicators_lines)

    return indicators_lines


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
    default=Settings().raw_data_directory,
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
        dataset=DatasetLayout(root_dir=root_dir or Settings().raw_data_directory),
        coin=data_config.coin,
        currency=data_config.currency,
        target_period=data_config.period,
        from_date=data_config.from_date,
        to_date=data_config.to_date,
    )

    indicators_lines = _build_indicator_lines(
        config=indicators_config, fluctuations=fluctuations
    )

    _build_and_save_indicators_figure(
        fluctuations=fluctuations,
        indicators_lines=indicators_lines,
        output_path=output_path,
    )
