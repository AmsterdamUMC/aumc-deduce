import json
import os
from pathlib import PurePath, Path

import sys
from typing import Optional

from docdeid import Annotation, AnnotationSet

from deduce import Deduce


def regression_test(
    model: Deduce,
    examples_file: str,
    enabled: set[str],
    known_failures: Optional[set[int]] = None,
):
    if known_failures is None:
        known_failures = set()

    root = PurePath(os.path.dirname(__file__)).parent.parent
    path = root / PurePath("tests/data/regression_cases/" + examples_file)

    with open(Path(path), "rb") as file:
        examples = json.load(file)["examples"]

    failures = set()

    for example in examples:
        trues = AnnotationSet(
            Annotation(**annotation) for annotation in example["annotations"]
        )
        preds = model.deidentify(text=example["text"], enabled=enabled).annotations

        try:
            assert trues == preds
        except AssertionError:
            expected_str = annotation_set_to_str(trues)
            actual_str = annotation_set_to_str(preds)
            sys.stderr.write("\nMismatch in example " + str(example["id"])
                             + "\nExpected>" + expected_str + "<"
                             + "\nActual  >" + actual_str + "<\n")
            failures.add(example["id"])

    assert failures == known_failures


def annotation_set_to_str(annotation_set: AnnotationSet) -> str:
    ret = ""
    for annotation in annotation_set.sorted(by=("start_char", "end_char")):
        if annotation is None:
            ret += "[]"
        else:
            ret += "[" + annotation_to_str(annotation) + "]"

    return ret


def annotation_to_str(annotation: Annotation) -> str:
    return ("text : " + annotation.text +
            ", tag : " + annotation.tag +
            ", start_char: " + str(annotation.start_char) +
            ", end_char: " + str(annotation.end_char))


def annotators_from_group(model: Deduce, group: str) -> set[str]:
    return {name for name, _ in model.processors[group]}.union({group})


class TestRegression:
    def test_regression_name(self, model):
        regression_test(
            model=model,
            examples_file="names.json",
            enabled=annotators_from_group(model, "names"),
        )

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
