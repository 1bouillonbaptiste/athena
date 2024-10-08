import click

from athena.entrypoints.backtest import backtest
from athena.entrypoints.download import download
from athena.entrypoints.visualize import visualize


@click.group("athena")
def app():
    """Athena main group."""
    pass


app.add_command(download)
app.add_command(backtest)
app.add_command(visualize)


if __name__ == "__main__":
    app()
