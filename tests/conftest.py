import pytest

from deduce import Deduce


@pytest.fixture(scope="session")
def model():
    # "G:/divjk/cru/DEDUCE/GIT-share/jacob-git/amsterdamumc-deduce/amsterdamumc_config.json"
    # "G:/divjk/cru/DEDUCE/GIT-share/jacob-git/DeduceConf/aumc_config.json"
    return Deduce(config= "G:/divjk/cru/DEDUCE/GIT-share/jacob-git/DeduceConf/aumc_config.json", build_lookup_structs=True, load_base_config=False)