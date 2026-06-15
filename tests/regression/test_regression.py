import json
import os
from pathlib import Path
from typing import Optional

import pytest
from docdeid import Annotation, AnnotationSet

from deduce import Deduce

# Utility method to create an absolute and OS-independent path to the 
# examples file taking into account the different names used for
# the workspace / git directory
def create_path_to_examples(example_file_name):
    user_home = Path.home()
    user_name = os.environ.get("USER", os.environ.get("USERNAME"))
    if ("jacob" in user_name):
        workspace_dir = "workspace"
    else:
        workspace_dir = "git"
        
    examples_path = os.path.join(user_home, workspace_dir, "aumc-deduce", "tests", "data", "regression_cases", example_file_name)    
    return examples_path

def regression_test(
    model: Deduce,
    examples_file: str,
    enabled: set[str],
    known_failures: Optional[set[int]] = None,
):
    if known_failures is None:
        known_failures = set()
    
    path_to_example = create_path_to_examples(examples_file)
    with open(path_to_example, "rb") as file:
        examples = json.load(file)["examples"]

    failures = set()
    
    for example in examples:
        expected = AnnotationSet(
            Annotation(**annotation) for annotation in example["annotations"]
        )
        actual = model.deidentify(text=example["text"], metadata=None, enabled=enabled).annotations
        try:
            is_subset = expected.issubset(actual)
            assert is_subset == True
        except AssertionError:
            print("Failure for example Id: " + str(example["id"]))
            print("Expected: " + repr(expected))
            print("Actual  : " + repr(actual))
            failures.add(example["id"])
    
    if len(failures) != 0:
        print("Failures: ", failures)
        print("Known failures:", known_failures)
        assert failures == known_failures, "Mismatch between failures and known_failures"


def annotators_from_group(model: Deduce, group: str) -> set[str]:
    return {name for name, _ in model.processors[group]}.union({group})


class TestRegression:

    @pytest.mark.skip(reason="Test fails because of the newly introduced patient-data is not defined and included in the test")
    def test_regression_name(self, model):
        regression_test(
            model=model,
            examples_file="names.json",
            enabled=annotators_from_group(model, "names"),
        )

    @pytest.mark.skip(reason="Test fails because of the newly introduced patient-data is not defined and included in the test")
    def test_regression_location(self, model):
        regression_test(
            model=model,
            examples_file="locations.json",
            enabled=annotators_from_group(model, "locations"),
        )

    def test_regression_institution(self, model):
        regression_test(
            model=model,
            examples_file="institutions.json",
            enabled=annotators_from_group(model, "institutions"),
        )

    def test_regression_date(self, model):
        regression_test(
            model=model,
            examples_file="dates.json",
            enabled=annotators_from_group(model, "dates"),
        )

    def test_regression_age(self, model):
        regression_test(
            model=model,
            examples_file="ages.json",
            enabled=annotators_from_group(model, "ages"),
        )

    def test_regression_identifier(self, model):
        regression_test(
            model=model,
            examples_file="identifiers.json",
            enabled=annotators_from_group(model, "identifiers"),
        )

    def test_regression_phone(self, model):
        regression_test(
            model=model,
            examples_file="phone_numbers.json",
            enabled=annotators_from_group(model, "phone_numbers"),
        )

    def test_regression_email(self, model):
        regression_test(
            model=model,
            examples_file="emails.json",
            enabled=annotators_from_group(model, "email_addresses"),
        )

    def test_regression_url(self, model):
        regression_test(
            model=model,
            examples_file="urls.json",
            enabled=annotators_from_group(model, "urls"),
        )
