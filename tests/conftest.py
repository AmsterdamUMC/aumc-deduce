import os
from pathlib import PurePath, Path

import pytest

from deduce import Deduce


@pytest.fixture(scope="session")
def model():
    # relative to [tool.pytest.ini_options] defined in pyproject.toml
    root = PurePath(os.path.dirname(__file__)).parent
    path = root / PurePath("base_config.json")
    return Deduce(config=Path(path).as_posix(),
                  build_lookup_structs=False,
                  load_base_config=False)
