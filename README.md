# Athena

Hand-crafted library to create, analyze and deploy your trading strategies.

:warning: The development of this repo is still in progress


## Installation

:warning:
To use the deep-learning part of this project,
you need cuda 12.2 to be installed on your machine with recommended nvidia-535 drivers.

Install ```pyenv``` with python ```3.10.12```.

Create your own environment with :

```bash
pyenv virtualenv 3.10.12 athena
```

The project will then automatically configure itself with :

```bash
make setup
```

You can either

1. run your code using poetry with `poetry run script.py`
2. enter the dev container with `make build && make local` to run your code safely.

## Usage

### download


```bash
poetry run athena download \
    --coin btc \
    --currency usdt \
    --from-date 2020-01-01 \
    --to-date 2020-01-15 \
    --output-dir /data/athena \
    --overwrite
```
