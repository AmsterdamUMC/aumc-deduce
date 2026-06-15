import re
from unittest.mock import patch

import docdeid as dd
import pytest

from deduce.annotator import (
    BsnAnnotator,
    PatientMedicalRecordNumberAnnotator,
    ContextAnnotator,
    PatientNameAnnotator,
    PatientDataAnnotator,
    PhoneNumberAnnotator,
    RegexpPseudoAnnotator,
    TokenPatternAnnotator,
    _PatternPositionMatcher,
)
from deduce.person import Person
from deduce.tokenizer import DeduceTokenizer
from tests.helpers import linked_tokens

@pytest.fixture
def ds():
    ds = dd.ds.DsCollection()

    first_names = ["Andries", "pieter", "Aziz", "Bernard"]
    surnames = ["Meijer", "Smit", "Bakker", "Heerma"]

    ds["first_names"] = dd.ds.LookupSet()
    ds["first_names"].add_items_from_iterable(items=first_names)

    ds["surnames"] = dd.ds.LookupSet()
    ds["surnames"].add_items_from_iterable(items=surnames)

    return ds


@pytest.fixture
def tokenizer():
    return DeduceTokenizer()


@pytest.fixture
def regexp_pseudo_doc(tokenizer):

    return dd.Document(
        text="De patient is Na 12 jaar gestopt met medicijnen.",
        tokenizers={"default": tokenizer},
    )


@pytest.fixture
def pattern_doc(tokenizer):
    return dd.Document(
        text="De man heet Andries Meijer-Heerma, voornaam Andries.",
        tokenizers={"default": tokenizer},
    )


@pytest.fixture
def bsn_doc():
    d = dd.DocDeid()

    return d.deidentify(
        text="Geldige voorbeelden zijn: 111222333 en 123456782. \n"
        "Patientnummer is 01234, en ander id 01234567890."
    )


@pytest.fixture
def phone_number_doc():
    d = dd.DocDeid()

    return d.deidentify(
        text="Telefoonnummers zijn 0314-555555, (088 755 55 55) of (06)55555555, "
        "maar 065555 is te kort en 065555555555 is te lang. "
        "Verwijsnummer is 0800-9003."
    )


@pytest.fixture
def surname_pattern():
    return linked_tokens(["Van der", "Heide", "-", "Ginkel"])


def token(text: str):
    return dd.Token(text=text, start_char=0, end_char=len(text))


class TestPositionMatcher:
    
    def test_non_existing_function(self):
        with pytest.raises(NotImplementedError) as expected_exception:
            _PatternPositionMatcher.match({"non-existing-function": "test"}, token=token("test"))
        assert "No known logic for pattern non-existing-function" in str(expected_exception.value)
    
    def test_value_error(self):
        with pytest.raises(ValueError) as expected_exception:
            _PatternPositionMatcher.match({"value_1": "test", "value_2": "test"}, token=token("test"))
        assert "Cannot parse token pattern ({'value_1': 'test', 'value_2': 'test'}) with more than 1 key" in str(expected_exception.value)
        
    def test_deprecation_warning(self):
        with pytest.deprecated_call(): 
            _PatternPositionMatcher.match({"is_initial": "test"}, token=token("test"))
    
    def test_equal(self):
        assert _PatternPositionMatcher.match({"equal": "test"}, token=token("test"))
        assert not _PatternPositionMatcher.match({"equal": "_"}, token=token("test"))

    def test_re_match(self):
        assert _PatternPositionMatcher.match({"re_match": "[a-z]"}, token=token("abc"))
        assert _PatternPositionMatcher.match(
            {"re_match": "[a-z]"}, token=token("abc123")
        )
        assert not _PatternPositionMatcher.match({"re_match": "[a-z]"}, token=token(""))
        assert not _PatternPositionMatcher.match(
            {"re_match": "[a-z]"}, token=token("123")
        )
        assert not _PatternPositionMatcher.match(
            {"re_match": "[a-z]"}, token=token("123abc")
        )

    def test_is_initials(self):

        assert _PatternPositionMatcher.match({"is_initials": True}, token=token("A"))
        assert _PatternPositionMatcher.match({"is_initials": True}, token=token("AB"))
        assert _PatternPositionMatcher.match({"is_initials": True}, token=token("ABC"))
        assert _PatternPositionMatcher.match({"is_initials": True}, token=token("ABCD"))
        assert not _PatternPositionMatcher.match(
            {"is_initials": True}, token=token("ABCDE")
        )
        assert not _PatternPositionMatcher.match({"is_initials": True}, token=token(""))
        assert not _PatternPositionMatcher.match(
            {"is_initials": True}, token=token("abcd")
        )
        assert not _PatternPositionMatcher.match(
            {"is_initials": True}, token=token("abcde")
        )

    def test_match_like_name(self):
        pattern_position = {"like_name": True}

        assert _PatternPositionMatcher.match(pattern_position, token=token("Diederik"))
        assert not _PatternPositionMatcher.match(pattern_position, token=token("Le"))
        assert not _PatternPositionMatcher.match(
            pattern_position, token=token("diederik")
        )
        assert not _PatternPositionMatcher.match(
            pattern_position, token=token("Diederik3")
        )

    def test_match_lookup(self, ds):
        assert _PatternPositionMatcher.match(
            {"lookup": "first_names"}, token=token("Andries"), ds=ds
        )
        assert not _PatternPositionMatcher.match(
            {"lookup": "first_names"}, token=token("andries"), ds=ds
        )
        assert not _PatternPositionMatcher.match(
            {"lookup": "surnames"}, token=token("Andries"), ds=ds
        )
        assert not _PatternPositionMatcher.match(
            {"lookup": "first_names"}, token=token("Smit"), ds=ds
        )
        assert _PatternPositionMatcher.match(
            {"lookup": "surnames"}, token=token("Smit"), ds=ds
        )
        assert not _PatternPositionMatcher.match(
            {"lookup": "surnames"}, token=token("smit"), ds=ds
        )

    def test_match_neg_lookup(self, ds):
        assert not _PatternPositionMatcher.match(
            {"neg_lookup": "first_names"}, token=token("Andries"), ds=ds
        )
        assert _PatternPositionMatcher.match(
            {"neg_lookup": "first_names"}, token=token("andries"), ds=ds
        )
        assert _PatternPositionMatcher.match(
            {"neg_lookup": "surnames"}, token=token("Andries"), ds=ds
        )
        assert _PatternPositionMatcher.match(
            {"neg_lookup": "first_names"}, token=token("Smit"), ds=ds
        )
        assert not _PatternPositionMatcher.match(
            {"neg_lookup": "surnames"}, token=token("Smit"), ds=ds
        )
        assert _PatternPositionMatcher.match(
            {"neg_lookup": "surnames"}, token=token("smit"), ds=ds
        )

    def test_match_and(self):
        assert _PatternPositionMatcher.match(
            {"and": [{"equal": "Abcd"}, {"like_name": True}]},
            token=token("Abcd"),
            ds=ds,
        )
        assert not _PatternPositionMatcher.match(
            {"and": [{"equal": "dcef"}, {"like_name": True}]},
            token=token("Abcd"),
            ds=ds,
        )
        assert not _PatternPositionMatcher.match(
            {"and": [{"equal": "A"}, {"like_name": True}]}, token=token("A"), ds=ds
        )
        assert not _PatternPositionMatcher.match(
            {"and": [{"equal": "b"}, {"like_name": True}]}, token=token("a"), ds=ds
        )

    def test_match_or(self):
        assert _PatternPositionMatcher.match(
            {"or": [{"equal": "Abcd"}, {"like_name": True}]}, token=token("Abcd"), ds=ds
        )
        assert _PatternPositionMatcher.match(
            {"or": [{"equal": "dcef"}, {"like_name": True}]}, token=token("Abcd"), ds=ds
        )
        assert _PatternPositionMatcher.match(
            {"or": [{"equal": "A"}, {"like_name": True}]}, token=token("A"), ds=ds
        )
        assert not _PatternPositionMatcher.match(
            {"or": [{"equal": "b"}, {"like_name": True}]}, token=token("a"), ds=ds
        )


class TestTokenPatternAnnotator:
    
    def test_error_empty_ds(self):
        pattern = [{"lookup": "first_names"}, {"like_name": True}]
        with pytest.raises(RuntimeError) as expected_exception:
            token_pattern_annotator = TokenPatternAnnotator(pattern=pattern, ds=None, tag="_")
        assert "Created pattern with lookup in TokenPatternAnnotator, but no lookup structures provided." in str(expected_exception.value)
        
    
    def test_mismatch_lookup_type(self, pattern_doc, ds):
        pattern = [{"lookup": "first_names"}, {"like_name": True}]
        ds["first_names"] = "Incorrect typem (str)"
        with pytest.raises(ValueError) as expected_exception:
            token_pattern_annotator = TokenPatternAnnotator(pattern=pattern, ds=ds, tag="_")
        assert "Expected a LookupSet, but got a <class 'str'>" in str(expected_exception.value)    
    
    def test_match_sequence(self, pattern_doc, ds):
        pattern = [{"lookup": "first_names"}, {"like_name": True}]

        tpa = TokenPatternAnnotator(pattern=[{}], ds=ds, tag="_")

        assert tpa._match_sequence(
            pattern_doc.text, start_token=pattern_doc.get_tokens()[3], pattern=pattern
        ) == dd.Annotation(text="Andries Meijer", start_char=12, end_char=26, tag="_")
        assert (
            tpa._match_sequence(
                pattern_doc.text,
                start_token=pattern_doc.get_tokens()[7],
                pattern=pattern,
            )
            is None
        )

    def test_match_sequence_left(self, pattern_doc, ds):
        pattern = [{"lookup": "first_names"}, {"like_name": True}]

        tpa = TokenPatternAnnotator(pattern=[{}], ds=ds, tag="_")

        assert tpa._match_sequence(
            pattern_doc.text,
            start_token=pattern_doc.get_tokens()[4],
            pattern=pattern,
            direction="left",
        ) == dd.Annotation(text="Andries Meijer", start_char=12, end_char=26, tag="_")

        assert (
            tpa._match_sequence(
                pattern_doc.text,
                start_token=pattern_doc.get_tokens()[8],
                direction="left",
                pattern=pattern,
            )
            is None
        )

    def test_match_sequence_skip(self, pattern_doc, ds):
        pattern = [{"lookup": "surnames"}, {"like_name": True}]

        tpa = TokenPatternAnnotator(pattern=[{}], ds=ds, tag="_")

        assert tpa._match_sequence(
            pattern_doc.text,
            start_token=pattern_doc.get_tokens()[4],
            pattern=pattern,
            skip={"-"},
        ) == dd.Annotation(text="Meijer-Heerma", start_char=20, end_char=33, tag="_")
        assert (
            tpa._match_sequence(
                pattern_doc.text,
                start_token=pattern_doc.get_tokens()[4],
                pattern=pattern,
                skip=set(),
            )
            is None
        )

    def test_annotate_token_pattern_annotator(self, pattern_doc, ds):
        pattern = [{"lookup": "first_names"}, {"like_name": True}]

        token_pattern_annotator  = TokenPatternAnnotator(pattern=pattern, ds=ds, tag="_")

        assert token_pattern_annotator.annotate(pattern_doc) == [
            dd.Annotation(text="Andries Meijer", start_char=12, end_char=26, tag="_")
        ]


class TestContextAnnotator:
    def test_apply_context_pattern(self, pattern_doc):
        annotator = ContextAnnotator(pattern=[])

        annotations = dd.AnnotationSet(
            [
                dd.Annotation(
                    text="Andries",
                    start_char=12,
                    end_char=19,
                    tag="voornaam",
                    start_token=pattern_doc.get_tokens()[3],
                    end_token=pattern_doc.get_tokens()[3],
                )
            ]
        )

        assert annotator._apply_context_pattern(
            pattern_doc.text,
            annotations,
            {
                "pattern": [{"like_name": True}],
                "direction": "right",
                "pre_tag": "voornaam",
                "tag": "{tag}+naam",
            },
        ) == dd.AnnotationSet(
            [
                dd.Annotation(
                    text="Andries Meijer",
                    start_char=12,
                    end_char=26,
                    tag="voornaam+naam",
                )
            ]
        )

    def test_apply_context_pattern_left(self, pattern_doc):
        annotator = ContextAnnotator(pattern=[])

        annotations = dd.AnnotationSet(
            [
                dd.Annotation(
                    text="Meijer",
                    start_char=20,
                    end_char=26,
                    tag="achternaam",
                    start_token=pattern_doc.get_tokens()[4],
                    end_token=pattern_doc.get_tokens()[4],
                )
            ]
        )

        assert annotator._apply_context_pattern(
            pattern_doc.text,
            annotations,
            {
                "pattern": [{"like_name": True}],
                "direction": "left",
                "pre_tag": "achternaam",
                "tag": "naam+{tag}",
            },
        ) == dd.AnnotationSet(
            [
                dd.Annotation(
                    text="Andries Meijer",
                    start_char=12,
                    end_char=26,
                    tag="naam+achternaam",
                )
            ]
        )

    def test_apply_context_pattern_skip(self, pattern_doc):
        annotator = ContextAnnotator(pattern=[])

        annotations = dd.AnnotationSet(
            [
                dd.Annotation(
                    text="Meijer",
                    start_char=20,
                    end_char=26,
                    tag="achternaam",
                    start_token=pattern_doc.get_tokens()[4],
                    end_token=pattern_doc.get_tokens()[4],
                )
            ]
        )

        assert annotator._apply_context_pattern(
            pattern_doc.text,
            annotations,
            {
                "pattern": [{"like_name": True}],
                "direction": "right",
                "skip": ["-"],
                "pre_tag": "achternaam",
                "tag": "{tag}+naam",
            },
        ) == dd.AnnotationSet(
            [
                dd.Annotation(
                    text="Meijer-Heerma",
                    start_char=20,
                    end_char=33,
                    tag="achternaam+naam",
                )
            ]
        )

    def test_annotate_multiple(self, pattern_doc):
        pattern = [
            {
                "pattern": [{"like_name": True}],
                "direction": "right",
                "pre_tag": "voornaam",
                "tag": "{tag}+naam",
            },
            {
                "pattern": [{"like_name": True}],
                "direction": "right",
                "skip": ["-"],
                "pre_tag": "achternaam",
                "tag": "{tag}+naam",
            },
        ]

        annotator = ContextAnnotator(pattern=pattern, iterative=False)

        annotations = dd.AnnotationSet(
            [
                dd.Annotation(
                    text="Andries",
                    start_char=12,
                    end_char=19,
                    tag="voornaam",
                    start_token=pattern_doc.get_tokens()[3],
                    end_token=pattern_doc.get_tokens()[3],
                )
            ]
        )

        assert annotator._annotate(pattern_doc.text, annotations) == dd.AnnotationSet(
            {
                dd.Annotation(
                    text="Andries Meijer-Heerma",
                    start_char=12,
                    end_char=33,
                    tag="voornaam+naam+naam",
                )
            }
        )

    def test_annotate_iterative(self, pattern_doc):
        pattern = [
            {
                "pattern": [{"like_name": True}],
                "direction": "right",
                "skip": ["-"],
                "pre_tag": ["naam", "voornaam"],
                "tag": "{tag}+naam",
            }
        ]

        annotator = ContextAnnotator(pattern=pattern, iterative=True)

        annotations = dd.AnnotationSet(
            [
                dd.Annotation(
                    text="Andries",
                    start_char=12,
                    end_char=19,
                    tag="voornaam",
                    start_token=pattern_doc.get_tokens()[3],
                    end_token=pattern_doc.get_tokens()[3],
                )
            ]
        )

        assert annotator._annotate(pattern_doc.text, annotations) == dd.AnnotationSet(
            {
                dd.Annotation(
                    text="Andries Meijer-Heerma",
                    start_char=12,
                    end_char=33,
                    tag="voornaam+naam+naam",
                )
            }
        )


class TestPatientNameAnnotator:
    
    
    def test_metadata_none_or_empty(self, tokenizer):
        
        metadata = None
        patient_name_annotator = PatientNameAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)
        annotation_list = patient_name_annotator.annotate(doc)
        assert annotation_list == []
        
        metadata = []
        doc = dd.Document(text="_", metadata=metadata)
        annotation_list = patient_name_annotator.annotate(doc)
        assert annotation_list == []
        
            
    def test_match_first_name_multiple(self, tokenizer):

        metadata = {"patient":  Person(first_names=["Jan", "Adriaan"],
                                       initials="",
                                       surname=[""],
                                       partnername=[""],
                                       given_name=[],
                                       person_id="",
                                       street=[],
                                       country=[],
                                       location=[])}
        tokens = linked_tokens(["Jan", "Adriaan"])
        ann = PatientNameAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)

        assert ann._match_first_names(doc=doc, token=tokens[0]) == (
            tokens[0],
            tokens[0],
        )

        assert ann._match_first_names(doc=doc, token=tokens[1]) == (
            tokens[1],
            tokens[1],
        )

    def test_match_first_name_fuzzy(self, tokenizer):

        metadata = {"patient": Person(first_names=["Adriaan"],
                                       initials="",
                                       surname=[""],
                                       partnername=[""],
                                       given_name=[],
                                       person_id="",
                                       street=[],
                                       country=[],
                                       location=[])}
        tokens = linked_tokens(["Adriana"])

        ann = PatientNameAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)

        assert ann._match_first_names(doc=doc, token=tokens[0]) == (
            tokens[0],
            tokens[0],
        )

    def test_match_first_name_fuzzy_short(self, tokenizer):

        metadata = {"patient": Person(first_names=["Jan"],
                                       initials="",
                                       surname=[""],
                                       partnername=[""],
                                       given_name=[],
                                       person_id="",
                                       street=[],
                                       country=[],
                                       location=[])}
        tokens = linked_tokens(["Dan"])

        ann = PatientNameAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)

        assert ann._match_first_names(doc=doc, token=tokens[0]) is None

    def test_match_initial_from_name(self, tokenizer):

        metadata = {"patient": Person(first_names=["Jan", "Adriaan"],
                                       initials="",
                                       surname=[""],
                                       partnername=[""],
                                       given_name=[],
                                       person_id="",
                                       street=[],
                                       country=[],
                                       location=[])}
        tokens = linked_tokens(["A", "J"])

        ann = PatientNameAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)

        assert ann._match_initial_from_name(doc=doc, token=tokens[0]) == (
            tokens[0],
            tokens[0],
        )

        assert ann._match_initial_from_name(doc=doc, token=tokens[1]) == (
            tokens[1],
            tokens[1],
        )

    def test_match_initial_from_name_with_period(self, tokenizer):
        metadata = {"patient": Person(first_names=["Jan", "Adriaan"],
                                     initials="",
                                     surname=[""],
                                     partnername=[""],
                                     given_name=[],
                                     person_id="",
                                     street=[],
                                     country=[],
                                     location=[])}
        tokens = linked_tokens(["J", ".", "A", "."])

        ann = PatientNameAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)

        assert ann._match_initial_from_name(doc=doc, token=tokens[0]) == (
            tokens[0],
            tokens[1],
        )

        assert ann._match_initial_from_name(doc=doc, token=tokens[2]) == (
            tokens[2],
            tokens[3],
        )

    def test_match_initial_from_name_no_match(self, tokenizer):
        metadata = {"patient": Person(first_names=["Jan", "Adriaan"],
                                     initials="",
                                     surname=[""],
                                     partnername=[""],
                                     given_name=[],
                                     person_id="",
                                     street=[],
                                     country=[],
                                     location=[])}
        tokens = linked_tokens(["F", "T"])

        ann = PatientNameAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)

        assert ann._match_initial_from_name(doc=doc, token=tokens[0]) is None
        assert ann._match_initial_from_name(doc=doc, token=tokens[1]) is None

    def test_match_initials(self, tokenizer):
        metadata = {"patient": Person(first_names=[],
                                         initials="AFTH",
                                         surname=[""],
                                         partnername=[""],
                                         given_name=[],
                                         person_id="",
                                         street=[],
                                         country=[],
                                         location=[])}
        tokens = linked_tokens(["AFTH", "THFA"])

        ann = PatientNameAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)

        assert ann._match_initials(doc=doc, token=tokens[0]) == (tokens[0], tokens[0])
        assert ann._match_initials(doc=doc, token=tokens[1]) is None

    def test_match_surname_equal(self, tokenizer, surname_pattern):

        metadata = {"surname_pattern": surname_pattern}
        tokens = linked_tokens(["Van der", "Heide", "-", "Ginkel", "is", "de", "naam"])

        ann = PatientNameAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)

        with patch.object(tokenizer, "tokenize", return_value=surname_pattern):

            assert ann._match_surname(doc=doc, token=tokens[0]) == (
                tokens[0],
                tokens[3],
            )

    def test_match_surname_longer_than_tokens(self, tokenizer, surname_pattern):

        metadata = {"surname_pattern": surname_pattern}
        tokens = linked_tokens(["Van der", "Heide"])

        ann = PatientNameAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)

        with patch.object(tokenizer, "tokenize", return_value=surname_pattern):

            assert ann._match_surname(doc=doc, token=tokens[0]) is None

    def test_match_surname_fuzzy(self, tokenizer, surname_pattern):

        metadata = {"surname_pattern": surname_pattern}
        tokens = linked_tokens(["Van der", "Heijde", "-", "Ginkle", "is", "de", "naam"])

        ann = PatientNameAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)

        with patch.object(tokenizer, "tokenize", return_value=surname_pattern):

            assert ann._match_surname(doc=doc, token=tokens[0]) == (
                tokens[0],
                tokens[3],
            )

    def test_match_surname_unequal_first(self, tokenizer, surname_pattern):

        metadata = {"surname_pattern": surname_pattern}
        tokens = linked_tokens(["v/der", "Heide", "-", "Ginkel", "is", "de", "naam"])

        ann = PatientNameAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)

        with patch.object(tokenizer, "tokenize", return_value=surname_pattern):

            assert ann._match_surname(doc=doc, token=tokens[0]) is None

    def test_match_surname_unequal_first_fuzzy(self, tokenizer, surname_pattern):

        metadata = {"surname_pattern": surname_pattern}
        tokens = linked_tokens(["Van den", "Heide", "-", "Ginkel", "is", "de", "naam"])

        ann = PatientNameAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)

        with patch.object(tokenizer, "tokenize", return_value=surname_pattern):

            assert ann._match_surname(doc=doc, token=tokens[0]) == (
                tokens[0],
                tokens[3],
            )

    def test_annotate_first_name(self, tokenizer):

        metadata = {
            "patient": Person(first_names=["Jan", "Johan"],
                                         initials="JJ",
                                         surname=["Jansen"],
                                         partnername=[""],
                                         given_name=[],
                                         person_id="",
                                         street=[],
                                         country=[],
                                         location=[])
        }
        text = "De patient heet Jan"
        tokens = tokenizer.tokenize(text)

        ann = PatientNameAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text=text, metadata=metadata)

        with patch.object(doc, "get_tokens", return_value=tokens):
            with patch.object(
                tokenizer, "tokenize", return_value=linked_tokens(["Jansen"])
            ):
                annotations = ann.annotate(doc)

        assert annotations == [
            dd.Annotation(
                text="Jan",
                start_char=16,
                end_char=19,
                tag="voornaam_patient",
            )
        ]

    def test_annotate_initials_from_name(self, tokenizer):
        metadata = {
            "patient": Person(first_names=["Jan", "Johan"],
                              initials="JJ",
                              surname=["Jansen"],
                              partnername=[""],
                              given_name=[],
                              person_id="",
                              street=[],
                              country=[],
                              location=[])
        }
        text = "De patient heet JJ"
        tokens = tokenizer.tokenize(text)

        ann = PatientNameAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text=text, metadata=metadata)

        with patch.object(doc, "get_tokens", return_value=tokens):
            with patch.object(
                tokenizer, "tokenize", return_value=linked_tokens(["Jansen"])
            ):
                annotations = ann.annotate(doc)

        assert annotations == [
            dd.Annotation(
                text="JJ",
                start_char=16,
                end_char=18,
                tag="initiaal_patient",
            )
        ]

    def test_annotate_initial(self, tokenizer):

        metadata = {
            "patient": Person(first_names=["Jan", "Johan"],
                              initials="JJ",
                              surname=["Jansen"],
                              partnername=[""],
                              given_name=[],
                              person_id="",
                              street=[],
                              country=[],
                              location=[])
        }
        text = "De patient heet J."
        tokens = tokenizer.tokenize(text)

        ann = PatientNameAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text=text, metadata=metadata)

        with patch.object(doc, "get_tokens", return_value=tokens):
            with patch.object(
                tokenizer, "tokenize", return_value=linked_tokens(["Jansen"])
            ):
                annotations = ann.annotate(doc)

        assert annotations == [
            dd.Annotation(
                text="J.",
                start_char=16,
                end_char=18,
                tag="initiaal_patient",
            )
        ]

    def test_annotate_surname(self, tokenizer):
        metadata = {
            "patient": Person(first_names=["Jan", "Johan"],
                              initials="JJ",
                              surname=["Jansen"],
                              partnername=[""],
                              given_name=[],
                              person_id="",
                              street=[],
                              country=[],
                              location=[])
        }
        text = "De patient heet Jansen"
        tokens = tokenizer.tokenize(text)

        ann = PatientNameAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text=text, metadata=metadata)

        with patch.object(doc, "get_tokens", return_value=tokens):
            with patch.object(
                tokenizer, "tokenize", return_value=linked_tokens(["Jansen"])
            ):
                annotations = ann.annotate(doc)

        assert annotations == [
            dd.Annotation(
                text="Jansen",
                start_char=16,
                end_char=22,
                tag="achternaam_patient",
            )
        ]


class TestPatientDataAnnotator:
    
    
    def test_metadata_none_or_empty_patient_name_annotator(self, tokenizer):
        
        metadata = None
        patient_name_annotator = PatientDataAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)
        annotation_list = patient_name_annotator.annotate(doc)
        assert annotation_list == []
        
        metadata = []
        doc = dd.Document(text="_", metadata=metadata)
        annotation_list = patient_name_annotator.annotate(doc)
        assert annotation_list == []
        
    def test_extend_patient_tokens(self, tokenizer):
        metadata = {"patient":  Person(first_names=[],
                                       initials="",
                                       surname=["bol", "HOL", "Güs", "hös", "ČUK"],
                                       partnername=[""],
                                       given_name=[],
                                       person_id="ID_EXTEND_PATIENT_TOKENS",
                                       street=[],
                                       country=[],
                                       location=[])}
        tokens = linked_tokens(["Dol", "Adriaan"])
        patient_data_annotator = PatientDataAnnotator(tokenizer=tokenizer, tag="_")
        extended_list = patient_data_annotator.extend_patient_tokens(metadata["patient"].surname)
        # TODO Ask if it is intentional that  'bol' (lower case only) is not extended with 'Bol' (title case).
        # Ask how multi token strings (with Dutch surname prefixes are to be dealt with (e.g. 'de Boer'
        word_list = []
        for token_list in extended_list:
            for token in token_list:
                word_list.append(token.text)
        assert len(word_list) == 16
           
    def test_match_first_name_multiple(self, tokenizer):

        metadata = {"patient":  Person(first_names=["Jan", "Adriaan"],
                                       initials="",
                                       surname=[""],
                                       partnername=[""],
                                       given_name=[],
                                       person_id="ID_MATCH_FIRST_NAME_MULTIPLE",
                                       street=[],
                                       country=[],
                                       location=[])}
        tokens = linked_tokens(["Jan", "Adriaan"])
        ann = PatientDataAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="De patient Jan Adriaan woont ...", metadata=metadata)

        assert ann._match_first_names(doc=doc, token=tokens[0]) == (
            tokens[0],
            tokens[0],
        )

        assert ann._match_first_names(doc=doc, token=tokens[1]) == (
            tokens[1],
            tokens[1],
        )

    def test_match_first_name_fuzzy(self, tokenizer):

        metadata = {"patient": Person(first_names=["Adriaan"],
                                       initials="",
                                       surname=[""],
                                       partnername=[""],
                                       given_name=[],
                                       person_id="ID_MATCH_FIRST_NAME_FUZZY",
                                       street=[],
                                       country=[],
                                       location=[])}
        tokens = linked_tokens(["Adriana"])

        ann = PatientDataAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)

        assert ann._match_first_names(doc=doc, token=tokens[0]) == (
            tokens[0],
            tokens[0],
        )

    def test_match_first_name_fuzzy_short(self, tokenizer):

        metadata = {"patient": Person(first_names=["Jan"],
                                       initials="",
                                       surname=[""],
                                       partnername=[""],
                                       given_name=[],
                                       person_id="ID_MATCH_FIRST_NAME_FUZZY_SHORT",
                                       street=[],
                                       country=[],
                                       location=[])}
        tokens = linked_tokens(["Dan"])

        ann = PatientDataAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)

        assert ann._match_first_names(doc=doc, token=tokens[0]) is None

    def test_match_initial_from_name(self, tokenizer):

        metadata = {"patient": Person(first_names=["Jan", "Adriaan"],
                                       initials="",
                                       surname=[""],
                                       partnername=[""],
                                       given_name=[],
                                       person_id="ID_MATCH_INITIAL_FROM_NAME",
                                       street=[],
                                       country=[],
                                       location=[])}
        tokens = linked_tokens(["A", "J"])

        ann = PatientDataAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)

        assert ann._match_initial_from_name(doc=doc, token=tokens[0]) == (
            tokens[0],
            tokens[0],
        )

        assert ann._match_initial_from_name(doc=doc, token=tokens[1]) == (
            tokens[1],
            tokens[1],
        )

    def test_match_initial_from_name_with_period(self, tokenizer):
        metadata = {"patient": Person(first_names=["Jan", "Adriaan"],
                                     initials="",
                                     surname=[""],
                                     partnername=[""],
                                     given_name=[],
                                     person_id="ID_MATCH_INITIAL_FROM_NAME_WITH_PERIOD",
                                     street=[],
                                     country=[],
                                     location=[])}
        tokens = linked_tokens(["J", ".", "A", "."])

        ann = PatientDataAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)

        assert ann._match_initial_from_name(doc=doc, token=tokens[0]) == (
            tokens[0],
            tokens[1],
        )

        assert ann._match_initial_from_name(doc=doc, token=tokens[2]) == (
            tokens[2],
            tokens[3],
        )

        metadata = {"patient": Person(first_names=["Jan", "Adriaan"],
                                     initials="",
                                     surname=[""],
                                     partnername=[""],
                                     given_name=[],
                                     person_id="",
                                     street=[],
                                     country=[],
                                     location=[])}
        tokens = linked_tokens(["F", "T"])

        ann = PatientDataAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)

        assert ann._match_initial_from_name(doc=doc, token=tokens[0]) is None
        assert ann._match_initial_from_name(doc=doc, token=tokens[1]) is None

        metadata = {"patient": Person(first_names=[],
                                         initials="AFTH",
                                         surname=[""],
                                         partnername=[""],
                                         given_name=[],
                                         person_id="",
                                         street=[],
                                         country=[],
                                         location=[])}
        tokens = linked_tokens(["AFTH", "THFA"])

        ann = PatientDataAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)

        assert ann._match_initials(doc=doc, token=tokens[0]) == (tokens[0], tokens[0])
        assert ann._match_initials(doc=doc, token=tokens[1]) is None

    def test__match_surname(self, tokenizer):
        # Test for the ( _match_surname ) method. This method could be replaced with a 
        # common method for surname, streets and locations. There is  a lot of duplicate code 
        # in these match methods.
        metadata = {"patient": Person(first_names=[],
                                         initials="",
                                         surname=["AAAAA"],
                                         partnername=[""],
                                         given_name=[],
                                         person_id="",
                                         street=[],
                                         country=[],
                                         location=[])}
        
        tokens = linked_tokens(["AAAAA", "BBBBB"])

        ann = PatientDataAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)
        ann.initialize_metadata(doc)
        assert ann._match_surname(doc=doc, token=tokens[0]) == (
                tokens[0],
                tokens[0],
            )
        
        metadata["patient"].surname = [""]
        doc = dd.Document(text="_", metadata=metadata)
        ann.initialize_metadata(doc)
        assert ann._match_surname(doc=doc, token=tokens[0]) is None
         
        metadata["patient"].surname = []
        doc = dd.Document(text="_", metadata=metadata)
        ann.initialize_metadata(doc)
        assert ann._match_surname(doc=doc, token=tokens[0]) is None

        # use one of the skip variables
        metadata["patient"].surname = ["Puk"]
        tokens = linked_tokens(["", ""])
        doc = dd.Document(text="_", metadata=metadata)
        ann.initialize_metadata(doc)
        assert ann._match_surname(doc=doc, token=tokens[0]) is None
        

    def test_match_surname_longer_than_tokens(self, tokenizer, surname_pattern):

        metadata = {"surname_pattern": surname_pattern}
        tokens = linked_tokens(["Van der", "Heide"])

        ann = PatientDataAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)

        with patch.object(tokenizer, "tokenize", return_value=surname_pattern):

            assert ann._match_surname(doc=doc, token=tokens[0]) is None

    def test_match_surname_unequal_first(self, tokenizer, surname_pattern):

        metadata = {"surname_pattern": surname_pattern}
        tokens = linked_tokens(["v/der", "Heide", "-", "Ginkel", "is", "de", "naam"])

        ann = PatientDataAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)

        with patch.object(tokenizer, "tokenize", return_value=surname_pattern):

            assert ann._match_surname(doc=doc, token=tokens[0]) is None

     # TODO consult Tom to ask him what to do with the prefix names
    @pytest.mark.skip("Skipping for now")
    def test_match_surname_unequal_first_fuzzy(self, tokenizer, surname_pattern):

        metadata = {"surname_pattern": surname_pattern}
        tokens = linked_tokens(["Van den", "Heide", "-", "Ginkel", "is", "de", "naam"])

        ann = PatientDataAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text="_", metadata=metadata)

        with patch.object(tokenizer, "tokenize", return_value=surname_pattern):

            assert ann._match_surname(doc=doc, token=tokens[0]) == (
                tokens[0],
                tokens[3],
            )

    def test_annotate_first_name(self, tokenizer):

        metadata = {
            "patient": Person(first_names=["Jan", "Johan"],
                                         initials="JJ",
                                         surname=["Jansen"],
                                         partnername=[""],
                                         given_name=[],
                                         person_id="TEST_ANNOTATE_FIRST_NAME",
                                         street=[],
                                         country=[],
                                         location=[])
        }
        text = "De patient heet Jan"
        tokens = tokenizer.tokenize(text)

        ann = PatientDataAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text=text, metadata=metadata)

        with patch.object(doc, "get_tokens", return_value=tokens):
            with patch.object(
                tokenizer, "tokenize", return_value=linked_tokens(["Jansen"])
            ):
                annotations = ann.annotate(doc)

        assert annotations == [
            dd.Annotation(
                text="Jan",
                start_char=16,
                end_char=19,
                tag="voornaam_patient",
            )
        ]

    def test_lower_case_surnames(self, tokenizer):
        metadata = {
            "patient": Person(first_names=["Jan", "Johan"],
                              initials="JJ",
                              surname=["jansen", "nelissen"],
                              partnername=[""],
                              given_name=[],
                              person_id="ID_MIXED_CASE_SURNAMES",
                              street=[],
                              country=[],
                              location=[])
        }
        text = "De patient heet jan johan jansen nelissen"
        tokens = tokenizer.tokenize(text)
        patient_data_annotator = PatientDataAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text=text, metadata=metadata)

    def test_annotate_initials_from_name(self, tokenizer):
        metadata = {
            "patient": Person(first_names=["Jan", "Johan"],
                              initials="JJ",
                              surname=["Jansen"],
                              partnername=[""],
                              given_name=[],
                              person_id="ID_ANNOTATE_INITIALS_FROM_NAME",
                              street=[],
                              country=[],
                              location=[])
        }
        text = "De patient heet JJ"
        tokens = tokenizer.tokenize(text)

        ann = PatientDataAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text=text, metadata=metadata)

        with patch.object(doc, "get_tokens", return_value=tokens):
            with patch.object(
                tokenizer, "tokenize", return_value=linked_tokens(["Jansen"])
            ):
                annotations = ann.annotate(doc)

        assert annotations == [
            dd.Annotation(
                text="JJ",
                start_char=16,
                end_char=18,
                tag="initiaal_patient",
            )
        ]

    # TODO consult Tom to ask him what to do with patient initials in the text.
    @pytest.mark.skip("Skipping for now")
    def test_annotate_initial(self, tokenizer):

        metadata = {
            "patient": Person(first_names=["Jan", "Johan"],
                              initials="JJ",
                              surname=["Jansen"],
                              partnername=[""],
                              given_name=[],
                              person_id="ID_ANNOTATE_INITIAL",
                              street=[],
                              country=[],
                              location=[])
        }
        text = "De patient heet J."
        tokens = tokenizer.tokenize(text)

        ann = PatientDataAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text=text, metadata=metadata)

        with patch.object(doc, "get_tokens", return_value=tokens):
            with patch.object(
                tokenizer, "tokenize", return_value=linked_tokens(["Jansen"])
            ):
                annotations = ann.annotate(doc)

        assert annotations == [
            dd.Annotation(
                text="J.",
                start_char=16,
                end_char=18,
                tag="initiaal_patient",
            )
        ]

    def test_annotate_surname(self, tokenizer):
        metadata = {
            "patient": Person(first_names=["Jan", "Johan"],
                              initials="JJ",
                              surname=["Jansen"],
                              partnername=[""],
                              given_name=[],
                              person_id="ID_ANNOTATE_SURNAME",
                              street=[],
                              country=[],
                              location=[])
        }
        text = "De patient heet Jansen"
        tokens = tokenizer.tokenize(text)

        ann = PatientDataAnnotator(tokenizer=tokenizer, tag="_")
        doc = dd.Document(text=text, metadata=metadata)

        with patch.object(doc, "get_tokens", return_value=tokens):
            with patch.object(
                tokenizer, "tokenize", return_value=linked_tokens(["Jansen"])
            ):
                annotations = ann.annotate(doc)

        assert annotations == [
            dd.Annotation(
                text="Jansen",
                start_char=16,
                end_char=22,
                tag="achternaam_patient",
            )
        ]



class TestRegexpPseudoAnnotator:
    def test_is_word_char(self):

        assert RegexpPseudoAnnotator._is_word_char("a")
        assert RegexpPseudoAnnotator._is_word_char("abc")
        assert not RegexpPseudoAnnotator._is_word_char("123")
        assert not RegexpPseudoAnnotator._is_word_char(" ")
        assert not RegexpPseudoAnnotator._is_word_char("\n")
        assert not RegexpPseudoAnnotator._is_word_char(".")

    def test_get_previous_word(self):

        r = RegexpPseudoAnnotator(regexp_pattern="_", tag="_")

        assert r._get_previous_word(0, "12 jaar") == ""
        assert r._get_previous_word(1, "<12 jaar") == ""
        assert r._get_previous_word(8, "patient 12 jaar") == "patient"
        assert r._get_previous_word(7, "(sinds 12 jaar)") == "sinds"
        assert r._get_previous_word(11, "patient is 12 jaar)") == "is"

    def test_get_next(self):

        r = RegexpPseudoAnnotator(regexp_pattern="_", tag="_")

        assert r._get_next_word(7, "12 jaar") == ""
        assert r._get_next_word(7, "12 jaar, geleden") == ""
        assert r._get_next_word(7, "12 jaar geleden") == "geleden"
        assert r._get_next_word(7, "12 jaar geleden geopereerd") == "geleden"

    def test_validate_match(self, regexp_pseudo_doc):

        r = RegexpPseudoAnnotator(regexp_pattern="_", tag="_")
        pattern = re.compile(r"\d+ jaar")

        match = list(pattern.finditer(regexp_pseudo_doc.text))[0]

        assert r._validate_match(match, regexp_pseudo_doc)

    def test_validate_match_pre(self, regexp_pseudo_doc):

        r = RegexpPseudoAnnotator(
            regexp_pattern="_", tag="_", pre_pseudo={"sinds", "al", "vanaf"}
        )
        pattern = re.compile(r"\d+ jaar")

        match = list(pattern.finditer(regexp_pseudo_doc.text))[0]

        assert r._validate_match(match, regexp_pseudo_doc)

    def test_validate_match_post(self, regexp_pseudo_doc):

        r = RegexpPseudoAnnotator(
            regexp_pattern="_", tag="_", post_pseudo={"geleden", "getrouwd", "gestopt"}
        )
        pattern = re.compile(r"\d+ jaar")

        match = list(pattern.finditer(regexp_pseudo_doc.text))[0]

        assert not r._validate_match(match, regexp_pseudo_doc)

    def test_validate_match_lower(self, regexp_pseudo_doc):

        r = RegexpPseudoAnnotator(
            regexp_pattern="_", tag="_", pre_pseudo=["na"], lowercase=True
        )
        pattern = re.compile(r"\d+ jaar")

        match = list(pattern.finditer(regexp_pseudo_doc.text))[0]

        assert not r._validate_match(match, regexp_pseudo_doc)


class TestPatientMedicalRecordNumberAnnotator:
    # Length of the MRN is 7 so we use {5} with 1 leading and tailing digit.
    mrn_regexp = r"(\b)(\d(\D?\d\D?){5}\d)(\b)"
    capture_group = 2
    
    def test_non_continious_number(self):
        metadata = {"patient": Person(first_names=["Adriaan"],
                                       initials="",
                                       surname=[""],
                                       partnername=[""],
                                       given_name=[],
                                       person_id="0003344",
                                       street=[],
                                       country=[],
                                       location=[])}
        an = PatientMedicalRecordNumberAnnotator(mrn_regexp=TestPatientMedicalRecordNumberAnnotator.mrn_regexp,
                                                 capture_group=TestPatientMedicalRecordNumberAnnotator.capture_group,
                                                 tag="_")
        doc = dd.Document("000.334.4.")
        doc.metadata = metadata
        annotations = an.annotate(doc)

        expected_annotations = [
            dd.Annotation(text="000.334.4", start_char=0, end_char=9, tag="_"),
        ]

        assert annotations == expected_annotations

class TestBsnAnnotator:
    
    bsn_regexp = r"(\b)(\d(\D?\d\D?){7}\d)(\b)"
    capture_group = 2
    
    def test_elfproef(self):
        an = BsnAnnotator(bsn_regexp=TestBsnAnnotator.bsn_regexp, capture_group=TestBsnAnnotator.capture_group, tag="_")

        assert an._elfproef("111222333")
        assert not an._elfproef("111222334")
        assert an._elfproef("123456782")
        assert not an._elfproef("123456783")

    def test_elfproef_wrong_length(self):
        an = BsnAnnotator(bsn_regexp=TestBsnAnnotator.bsn_regexp, capture_group=TestBsnAnnotator.capture_group, tag="_")
        assert False == an._elfproef("12345678")

    def test_elfproef_non_numeric(self):
        an = BsnAnnotator(bsn_regexp=TestBsnAnnotator.bsn_regexp, capture_group=TestBsnAnnotator.capture_group, tag="_")
        assert False == an._elfproef("test")

    def test_bsn_annotator(self, bsn_doc):
        bsn_annotator = BsnAnnotator(bsn_regexp=TestBsnAnnotator.bsn_regexp, capture_group=TestBsnAnnotator.capture_group, tag="_")
        annotations = bsn_annotator.annotate(bsn_doc)

        expected_annotations = [
            dd.Annotation(text="111222333", start_char=26, end_char=35, tag="_"),
            dd.Annotation(text="123456782", start_char=39, end_char=48, tag="_"),
        ]

        assert annotations == expected_annotations

    def test_annotate_with_nondigits(self, bsn_doc):
        an = BsnAnnotator(bsn_regexp=TestBsnAnnotator.bsn_regexp, capture_group=TestBsnAnnotator.capture_group, tag="_")
        # First a BSN like number which matches the reg-exp but fails the 11-proof
        doc = dd.Document("9999.97.611")
        annotations = an.annotate(doc)
        
        expected_annotations = []
        assert annotations == expected_annotations
        
        # a series of digits with non-numeric separators which match the reg-exp
        doc = dd.Document("9.7 14.8 8.1 13.8")
        annotations = an.annotate(doc)
        
        expected_annotations = []
        assert annotations == expected_annotations
        
        doc = dd.Document("9999.97.610")
        annotations = an.annotate(doc)
        

        expected_annotations = [
            dd.Annotation(text="9999.97.610", start_char=0, end_char=11, tag="_"),
        ]
        assert annotations == expected_annotations
        
        # Trailing and preceeding non-numeric group separators
        doc = dd.Document("   9999.97.300. ")
        annotations = an.annotate(doc)
        
        expected_annotations = [
            dd.Annotation(text="9999.97.300", start_char=3, end_char=14, tag="_"),
        ]
        assert annotations == expected_annotations
        
        doc = dd.Document("9999.97.099")
        annotations = an.annotate(doc)
        
        expected_annotations = [
            dd.Annotation(text="9999.97.099", start_char=0, end_char=11, tag="_"),
        ]
        assert annotations == expected_annotations
        
        doc = dd.Document("9999-95-108")
        annotations = an.annotate(doc)
        
        expected_annotations = [
            dd.Annotation(text="9999-95-108", start_char=0, end_char=11, tag="_"),
        ]
        assert annotations == expected_annotations
        
        doc = dd.Document("9999 95 777")
        annotations = an.annotate(doc)
        
        expected_annotations = [
            dd.Annotation(text="9999 95 777", start_char=0, end_char=11, tag="_"),
        ]
        assert annotations == expected_annotations


class TestPhoneNumberAnnotator:
    def test_annotate_defaults(self, phone_number_doc):
        an = PhoneNumberAnnotator(
            phone_regexp=r"(?<!\d)"
            r"(\(?(0031|\+31|0)"
            r"(1[035]|2[0347]|3[03568]|4[03456]|5[0358]|6|7|88|800|91|90[069]|"
            r"[1-5]\d{2})\)?)"
            r" ?-? ?"
            r"((\d{2,4}[ -]?)+\d{2,4})",
            tag="_",
        )
        annotations = an.annotate(phone_number_doc)

        expected_annotations = [
            dd.Annotation(text="0314-555555", start_char=21, end_char=32, tag="_"),
            dd.Annotation(text="088 755 55 55", start_char=35, end_char=48, tag="_"),
            dd.Annotation(text="(06)55555555", start_char=53, end_char=65, tag="_"),
            dd.Annotation(text="0800-9003", start_char=135, end_char=144, tag="_"),
        ]

        assert annotations == expected_annotations

    def test_annotate_short(self, phone_number_doc):
        an = PhoneNumberAnnotator(
            phone_regexp=r"(?<!\d)"
            r"(\(?(0031|\+31|0)"
            r"(1[035]|2[0347]|3[03568]|4[03456]|5[0358]|6|7|88|800|91|90[069]|"
            r"[1-5]\d{2})\)?)"
            r" ?-? ?"
            r"((\d{2,4}[ -]?)+\d{2,4})",
            min_digits=4,
            max_digits=8,
            tag="_",
        )
        annotations = an.annotate(phone_number_doc)

        expected_annotations = [
            dd.Annotation(text="065555", start_char=72, end_char=78, tag="_")
        ]

        assert annotations == expected_annotations

    def test_annotate_long(self, phone_number_doc):
        an = PhoneNumberAnnotator(
            phone_regexp=r"(?<!\d)"
            r"(\(?(0031|\+31|0)"
            r"(1[035]|2[0347]|3[03568]|4[03456]|5[0358]|6|7|88|800|91|90[069]|"
            r"[1-5]\d{2})\)?)"
            r" ?-? ?"
            r"((\d{2,4}[ -]?)+\d{2,4})",
            min_digits=11,
            max_digits=12,
            tag="_",
        )
        annotations = an.annotate(phone_number_doc)

        expected_annotations = [
            dd.Annotation(text="065555555555", start_char=93, end_char=105, tag="_")
        ]

        assert annotations == expected_annotations
