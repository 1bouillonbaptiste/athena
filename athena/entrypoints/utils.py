from pathlib import Path
import yaml


def load_config(filename: Path):
    """Load YAML file."""
    with open(filename, "r") as f:
        return yaml.safe_load(f)
