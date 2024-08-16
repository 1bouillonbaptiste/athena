# kouign amann




## Installation

Install ```pyenv``` with python ```3.12.5```.

Create your own environment with :

```bash
pyenv virtualenv 3.12.5 athena
```

The project will then automatically configure itself with :

```bash
make setup
```

## Usage

> [!WARNING]
> You need cuda 12.2 to be installed on your machine with recommended nvidia-535 drivers

Build the docker image using ```make build``` and then run it locally with ```make local```.
