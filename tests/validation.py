"""
Runs a validation test which compares records found in the tab-delimited file input-output-test.tsv. Each record
contains an input and the expected output. E.g.
My name is John Johnson and I live in Wisconsin.<TAB>My name is <PATIENT> and I live in <LOCATIE-1>.

The failing comparisons are sent to standard-output and together with some summary statistics.
"""
import os
from pathlib import Path
from deduce import Deduce
from deduce.person import Person
from _pytest.outcomes import fail


def annotators_from_group(model: Deduce, group: str) -> set[str]:
    return {name for name, _ in model.processors[group]}.union({group})

# Utility method to create an absolute and OS-independent path to the
# test file taking into account the different names used for
# the workspace / git directory
def create_path_to_examples(test_file_name):
    user_home = Path.home()

    workspace_dir = "git"

    examples_path = os.path.join(user_home, workspace_dir, "aumc-deduce", "tests", "regression", test_file_name)
    return examples_path

class TestValidationFile:
    def test_with_validation_file(self, model):
        file_to_test = create_path_to_examples("input-output-test.tsv")
        self.run_test_on_file(model, file_to_test)

    def test_prefix_names(self, model):
        file_to_test = create_path_to_examples("input-output-test-prefix-names.tsv")
        self.run_test_on_file(model, file_to_test)

    @staticmethod
    def run_test_on_file(model, file_to_test):
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
        mismatching_records_str = "[ "
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

            if len(columns) != 13:
                print("Missing column in record with ID  ", record_id)
                fail("Missing column in record with ID  ", record_id)
                continue

            failure_status = columns[1]
            first_names = columns[2].split()
            initials = columns[3]
            surname = columns[4].split()
            partner_name = columns[5].split()
            given_names = columns[6].split()
            patient_id = columns[7]
            street = columns[8].split()
            location = columns[9].split()
            country = columns[10].split()
            identifiable_input = columns[11].replace('\\t', '\u0009')
            expected_output = columns[12].replace('\\t', '\u0009')
            
            # The fields used in patient_details must match used for production runs. The used fields for production runs are defined
            # in the worker1 Python script in the aumc-deduce-prod project. The call to the patient_details and the call to the deidentify 
            # method are matched to the worker1 script. The deviant paramters have been replaced by empty lists.
            surname.extend(partner_name)
            patient_details = {"patient": Person(first_names=first_names,
                                                 initials=[],
                                                 surname=surname,
                                                 partnername=[],
                                                 given_name=[],
                                                 street=street,
                                                 location=location,
                                                 country=country,
                                                 patient_id=patient_id)}

            
            result_document = model.deidentify(text=identifiable_input, metadata=patient_details, disabled={'dates', 'age','longnumber'})

            actual_output = result_document.deidentified_text

            matching = expected_output == actual_output
            expected_failure = failure_status == 'F'
            
            if not matching:
                if expected_failure:
                    expected_failure_count += 1
                    print("\n==> Expected failure at record ", record_id)
                else:
                    mismatch_count += 1
                    mismatching_records_str += str(record_count) + " "
                    failed = True
                    print("\n==> Mismatch at record ", record_id)
                    print("Raw:      >" + identifiable_input + "<")
                    print("Expected: >" + expected_output + "<")
                    print("Actual:   >" + actual_output + "<")
            else:
                match_count += 1
                print("\n==> Match at record ", record_id)

        # assert mismatch_count == 0
        print("Done")
        print("==============================================================")
        print("Number of records   :", record_count)
        print("Number of matches   :", match_count)
        print("Number of mismatches:", mismatch_count)
        print("Expected mismatches :", expected_failure_count)
        print("==============================================================")
        
        assert failed == False, "\nAn unexpected failure / mismatch occurred at records " + mismatching_records_str + "].\nEither fix it or mark the record as failing with 'F'."
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
