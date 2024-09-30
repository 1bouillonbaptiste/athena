from athena.entrypoints.download import download
from athena.entrypoints.backtest import backtest

import click


@click.group("athena")
def app():
    """Athena main group."""
    pass


app.add_command(download)
app.add_command(backtest)


if __name__ == "__main__":
    app()
