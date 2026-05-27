import pytest
import os
from pathlib import Path

from deduce import Deduce
from attr._compat import get_generic_base


def get_checked_out_branch(config_path):
    head_dir = os.path.join(config_path, ".git", "HEAD")
    with Path(head_dir).open("r") as file: line_list = file.read().splitlines()
    checked_out_branch = ""
    for line in line_list:
        if line[0:4] == "ref:":
            checked_out_branch = line.partition("refs/heads/")[2]
    return checked_out_branch

@pytest.fixture(scope="session", autouse=True)
def model():
    user_home = Path.home()
    user_name = os.environ.get("USER", os.environ.get("USERNAME"))
    if ("jacob" in user_name):
        workspace_dir = "workspace"
    else:
        workspace_dir = "git"

    git_path = os.path.join(user_home, workspace_dir, "aumc-deduce-conf")
    checked_out_branch = get_checked_out_branch(git_path)
    EXPECTED_BRANCH = "non-confidential"
    if (checked_out_branch != EXPECTED_BRANCH):
        pytest.fail("Checked-out branch in the aumc-deduce-conf project must be '" + EXPECTED_BRANCH +"'")
    config_path = os.path.join(user_home, workspace_dir, "aumc-deduce-conf",  "aumc_config.json")
    # config_path = os.path.join(user_home, "workspace", "aumc-deduce", "base_config.json")
    print("Loading Deduce config file: ", config_path, flush=True)
    return Deduce(config=config_path, build_lookup_structs=True, load_base_config=False)
