"""
Runs a validation test which compares records found in the tab-delimited file input-output-test.tsv. Each record
contains an input and the expected output. E.g.
My name is John Johnson and I live in Wisconsin.<TAB>My name is <PATIENT> and I live in <LOCATIE-1>.

The failing comparisons are sent to standard-output and together with some summary statistics.
"""

from deduce import Deduce
from deduce.person import Person


def annotators_from_group(model: Deduce, group: str) -> set[str]:
    return {name for name, _ in model.processors[group]}.union({group})


class TestValidationFile:
    def test_with_validation_file(self, model):
        file_to_test = './regression/input-output-test.tsv'
        self.run_test_on_file(model, file_to_test)

    def test_prefix_names(self, model):
        file_to_test = './regression/input-output-test-prefix-names.tsv'
        self.run_test_on_file(model, file_to_test)

    def run_test_on_file(self, model, file_to_test):
        record_list = list()

        with open(file_to_test, mode="r", encoding="utf-8") as file:
            lines = file.readlines()
            count = 0
            for line in lines:
                # skip lines starting with the comment character
                if not line.strip().startswith(str("#")):
                    record_list.append(line.rstrip('\n'))
                count += 1
        print("\nNumber of records read: ", len(record_list))

        mismatch_count = 0
        match_count = 0
        expected_failure_count = 0
        record_count = 0
        failed = False
        for record in record_list:
            record_count += 1
            columns = record.split("\t")
            if len(columns) > 1:
                record_id = columns[0]
                # TODO deal with non numeric values in the record_id
                if int(record_id) != record_count:
                    raise ValueError("No consecutive record ID at approx. record ID: ", int(record_id),
                                     ". Value present: ", record_count)
            else:
                record_id = "Missing record ID at approx. record ID: ", record_count

            if len(columns) != 8:
                print("Missing column in record with ID  ", record_id)
                continue

            identifiable_input = columns[6]
            expected_output = columns[7]

            failure_status = columns[1]
            first_names = columns[2].strip()
            initials = columns[3].strip()
            surname = columns[4].strip()

            patient = Person.from_keywords(
                patient_first_names=first_names,
                patient_surname=surname,
            )

            metadata = {"patient": patient}

            result_document = model.deidentify(text=identifiable_input, metadata=metadata)

            actual_output = result_document.deidentified_text

            matching = expected_output == actual_output
            if not matching:
                if failure_status == 'F':
                    expected_failure_count += 1
                    print("\n==> Expected failure at record ", record_id)
                else:
                    mismatch_count += 1
                    failed = True
                    print("\n==> Mismatch at record ", record_id)
            else:
                match_count += 1
                print("\n==> Match at record ", record_id)
            print("Raw:      >" + identifiable_input + "<")
            print("Expected: >" + expected_output + "<")
            print("Actual:   >" + actual_output + "<")
        # assert mismatch_count == 0
        print("Done")
        print("==============================================================")
        print("Numer of records    :", record_count)
        print("Numer of matches    :", match_count)
        print("Number of mismatches:", mismatch_count)
        print("Expected mismatches :", expected_failure_count)

        print("==============================================================")
        # failures = set()

        #
        # for example in examples:
        #     trues = AnnotationSet(
        #         Annotation(**annotation) for annotation in example["annotations"]
        #     )
        #     predicates = model.deidentify(text=example["text"], enabled=enabled).annotations
        #
        #     try:
        #         assert trues == predicates
        #     except AssertionError:
        #         failures.add(example["id"])
