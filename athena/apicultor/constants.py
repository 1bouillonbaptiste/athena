import os

from athena import ProjectDirectory


def set_env(name: str, value: str):
    """Set environment variable."""
    os.environ[name] = value


if ProjectDirectory().credentials_file.exists():
    for line in ProjectDirectory().credentials_file.open("r"):
        name, value = line.replace("\n", "").split("=")
        set_env(name, value)

BINANCE_SECRET = os.environ.get("BINANCE_SECRET", None)
BINANCE_KEY = os.environ.get("BINANCE_KEY", None)
