import pytest

from deduce.tokenizer import DeduceTokenizer

from deduce.lookup_struct_loader import (
    load_common_word_lookup,
    load_eponymous_disease_lookup,
    load_prefix_lookup,
    load_surname_lookup,
    load_street_lookup,
    load_placename_lookup,
    load_hospital_lookup,
    load_whitelist_lookup,
    load_institution_lookup,
    load_first_name_lookup
)

@pytest.fixture
def tokenizer():
    return DeduceTokenizer()


class TestLookupStructLoader:
    
    def test_load_common_word_lookup(self):
        
        raw_itemset = {"common_word": ["AAA", "Bbb", "ccc", "ddd", "FF"],
                       "surname": ["CCC", "Ddd", "eee", "ff", "g"]}

        common_word = load_common_word_lookup(raw_itemset)

        assert len(common_word) == 3
        assert "AAA" in common_word
        assert "Bbb" in common_word
        assert "FF" in common_word
        assert "ccc" not in common_word
        assert "ddd" not in common_word
        assert "eee" not in common_word
        assert "ff" not in common_word
        assert "g" not in common_word
        
    def test_load_prefix_lookup(self):
        raw_itemset = {"prefix": ["drs", "mr"]}

        prefix_lookup = load_prefix_lookup(raw_itemset)
        
        assert len(prefix_lookup) == 4
        assert "drs" in prefix_lookup
        assert "Drs" in prefix_lookup
        assert "Mr" in prefix_lookup
        assert "mr" in prefix_lookup
        
        
    def test_load_whitelist_lookup(self):
        raw_itemset = {"surname": ["Vries", "Boer", "Crohn"],
                       "medical_term": ["Crohn"],
                       "stop_word": ["dan"],
                       "common_word": ["waarom"]}
        
        whitelist_lookup = load_whitelist_lookup(raw_itemset)
        
        assert len(whitelist_lookup) == 3
        assert "dan" in whitelist_lookup
        assert "waarom" in whitelist_lookup
        assert "crohn" in whitelist_lookup
        
        
    def test_load_surname_lookup(self, tokenizer):
        raw_itemset = {"surname": ["Vries", "Koert", "Crohn"],
                       "medical_term": ["Crohn"],
                       "stop_word": ["dan"],
                       "common_word": ["waarom"]} 
       
        surname_lookup_trie = load_surname_lookup(raw_itemset, tokenizer)

         # Only surnames with >= 5 characters are added capitalized
        assert ["Vries"] in surname_lookup_trie
        assert ["Koert"] in surname_lookup_trie
        assert ["VRIES"] in surname_lookup_trie
        assert ["KOERT"] in surname_lookup_trie
        assert ["Crohn"] not in surname_lookup_trie
        assert ["CROHN"] not in surname_lookup_trie
        
    
    
    def test_load_place_name_lookup(self, tokenizer):
        
        raw_itemset = {"placename": ["Tilburg", "  Mokum   ", "Not"],
                       "surname": ["Vries", "Koert", "Crohn"],
                       "medical_term": ["Crohn"],
                       "stop_word": ["dan"],
                       "common_word": ["waarom"]} 
       
        place_name_lookup_trie = load_placename_lookup(raw_itemset, tokenizer)
        assert ["Tilburg"] in place_name_lookup_trie
        assert ["Mokum"] in place_name_lookup_trie
        assert ["Not"] in place_name_lookup_trie
        
        
    def test_load_hospital_lookup(self, tokenizer):
        
        raw_itemset = {
                       "hospital": ["Universitair"],
                       "hospital_abbr": ["UMCU"]} 
       
        hospital_lookup_trie = load_hospital_lookup(raw_itemset, tokenizer)
        assert ["UMCU"] in hospital_lookup_trie
        assert ["Universitair"] in hospital_lookup_trie
        
        
    def test_load_institution_lookup(self, tokenizer):
        raw_itemset = {
                       "healthcare_institution": ["Mokummer"],
                       "surname": ["Vries", "Koert", "Crohn"],
                       "medical_term": ["Crohn"],
                       "stop_word": ["dan"],
                       "common_word": ["waarom"]} 
       
        institution_lookup_trie = load_institution_lookup(raw_itemset, tokenizer)
        assert ["Mokummer"] in institution_lookup_trie
        
        
    def test_load_first_name_lookup(self, tokenizer):
        raw_itemset = {
                       "first_name": ["Ad", "Adriaan"],
                       "surname": ["Vries", "Koert", "Crohn"],
                       "medical_term": ["Crohn"],
                       "stop_word": ["dan"],
                       "common_word": ["waarom"]}
        
        first_name_lookup_trie = load_first_name_lookup(raw_itemset, tokenizer)
        
        assert ["Adriaan"] in first_name_lookup_trie
        assert ["Ad"] in first_name_lookup_trie
        
    def test_load_eponymous_disease_lookup(self, tokenizer):
        
        raw_itemset = { "eponymous_disease": ['Guillian', ' Parkinson']} 
       
        eponymous_disease_lookup = load_eponymous_disease_lookup(raw_itemset, tokenizer)
        assert ["Parkinson"] in eponymous_disease_lookup
        assert ['Guillian'] in eponymous_disease_lookup
    
    # @pytest.mark.skip(reason="Unclear why the 'in' operator does not work here in contrast to the examples elsewhere")
    def test_load_street_lookup(self, tokenizer):
        
        raw_itemset = {"street": ["Willow", "Lenstra", "  Mayfair  ", "Not", " Not"]} 
       
        street_lookup_trie = load_street_lookup(raw_itemset, tokenizer)
        assert ["Willow"] in street_lookup_trie
        assert ["Lenstra"] in street_lookup_trie
        assert ["Mayfair"] in street_lookup_trie
        assert ["Not"] not in street_lookup_trie
