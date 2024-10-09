import os
from pathlib import Path

DATA_DIR = Path("/data/athena")


class ProjectContext:
    def __init__(self, root_dir: Path | None = None):
        if root_dir is None:
            try:  # works when running the code
                root_dir = Path(__file__).parent.parent.parent
            except NameError:  # `__file__` does not exist with python interpreter
                root_dir = os.getcwd()

        self._root_dir = root_dir

    @property
    def root_dir(self) -> Path:
        return self._root_dir

    @property
    def credentials_file(self) -> Path:
        return self._root_dir / ".credentials"

    @property
    def raw_data_directory(self) -> Path:
        return DATA_DIR / "raw_market_data"
