import click

from athena.entrypoints.backtest import backtest
from athena.entrypoints.download import download


@click.group("athena")
def app():
    """Athena main group."""
    pass


app.add_command(download)
app.add_command(backtest)


if __name__ == "__main__":
    app()
