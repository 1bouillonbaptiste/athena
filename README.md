# Athena

Hand-crafted library to create, analyze and deploy your trading strategies.
Only for educational purpose, don't sue me.

:warning: The development of this repo is still in progress. As of today you can
 - [x] download market data
 - [ ] create a strategy based on
     - [x] custom code
     - [ ] technical indicators
     - [ ] machine learning
 - [ ] backtest your strategy

Future work, not contractual, not exhaustive.
* create a new strategy from text-based input (👋 prompt engineers)


## Installation

:warning:
To use the deep-learning part of this project,
you need cuda 12.2 to be installed on your machine with recommended nvidia-535 drivers.

[Install pyenv](https://github.com/pyenv/pyenv-installer).

Create your own environment :

```bash
pyenv virtualenv 3.10.12 athena
```

The project will then automatically configure itself with :

```bash
make setup
```

You can either

1. run your code using poetry with `poetry run script.py`
2. enter the dev container with `make build && make local` to run your code (recommended for deep-learning).


## Usage

### download


```bash
poetry run athena download \
    --coin btc \
    --currency usdt \
    --from-date 2020-01-01 \
    --to-date 2020-01-15 \
    --output-dir /data/athena/market_data \
    --overwrite
```
