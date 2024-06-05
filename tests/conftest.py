import pytest

from deduce import Deduce


@pytest.fixture(scope="session")
def model():
    return Deduce(config="G:/divjk/cru/DEDUCE/GIT-share/jacob-git/DeduceConf-2/aumc_config.json", build_lookup_structs=True, load_base_config=False)