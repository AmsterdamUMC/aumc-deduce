import os
import io
from pathlib import Path
from unittest.mock import patch
from deduce.tokenizer import DeduceTokenizer

import docdeid as dd
import pytest


from deduce.lookup_structs import (
    cache_lookup_structs,
    load_lookup_structs_from_cache,
    load_raw_itemset,
    load_raw_itemsets,
    validate_lookup_struct_cache,
    get_lookup_structs,
    _CACHE_SUBDIR,
    _CACHE_FILE
)

DATA_PATH = Path(os.path.dirname(__file__)).parent / "data" / "lookup"
    

class TestLookupStruct:
        
    
    def test_get_lookup_structs(self):
        # Test loading the small set of lookup tables found in the /tests/data/lookup directory.
        tokenizer = DeduceTokenizer()
        
        deduce_version="2.5.0"
        
        lookup_structs = get_lookup_structs(DATA_PATH, tokenizer, deduce_version, ["lst_test", "lst_test_nested", "names/lst_prefix", "names/lst_street"], True, False) 
        
        assert len(lookup_structs) == 4
        assert "test" in lookup_structs.keys()
        assert "test_nested" in lookup_structs.keys()
        assert "prefix" in lookup_structs.keys()
        assert "street" in lookup_structs.keys()
        
        
    
    def test_load_raw_itemset_missing_directory(self):
        with pytest.raises(RuntimeError) as expected_exception:
            raw_itemset = load_raw_itemset(DATA_PATH / "src" / "lst_test_non_existant")
        
            assert "Cannot import lookup list " in str(expected_exception.value)
            assert "did not find items.txt or any sublists." in str(expected_exception.value)
    
            assert len(raw_itemset) == 0
    
    
    def test_load_raw_itemset(self):

        raw_itemset = load_raw_itemset(DATA_PATH / "src" / "lst_test")

        assert len(raw_itemset) == 5
        assert "de Vries" in raw_itemset
        assert "De Vries" in raw_itemset
        assert "Sijbrand" in raw_itemset
        assert "Sybrand" in raw_itemset
        assert "Pieters" in raw_itemset
        assert "Wolter" not in raw_itemset

    def test_load_raw_itemset_nested(self):

        raw_itemset = load_raw_itemset(DATA_PATH / "src" / "lst_test_nested")

        assert raw_itemset == {"a", "b", "c", "d"}

    def test_load_raw_itemsets(self):

        raw_itemsets = load_raw_itemsets(
            base_path=DATA_PATH, subdirs=["lst_test", "lst_test_nested"]
        )

        assert "test" in raw_itemsets
        assert len(raw_itemsets["test"]) == 5
        assert "test_nested" in raw_itemsets
        assert len(raw_itemsets["test_nested"]) == 4
        
        
    def test_validate_lookup_struct_cache_invalid_deduce_version(self):

        cache = {
            "deduce_version": "X.X.X",
            "saved_datetime": "2023-12-06 10:19:39.198133",
            "lookup_structs": "_",
        }

        class MockStats:
            st_mtime = 1000000000  # way in the past

        with patch("pathlib.Path.glob", return_value=[1, 2, 3]):
            with patch("os.stat", return_value=MockStats()):
                assert not validate_lookup_struct_cache(
                    cache=cache, base_path=DATA_PATH, deduce_version="2.5.0"
                )


    def test_validate_lookup_struct_cache_valid(self):

        cache = {
            "deduce_version": "2.5.0",
            "saved_datetime": "2023-12-06 10:19:39.198133",
            "lookup_structs": "_",
        }

        class MockStats:
            st_mtime = 1000000000  # way in the past

        with patch("pathlib.Path.glob", return_value=[1, 2, 3]):
            with patch("os.stat", return_value=MockStats()):
                assert validate_lookup_struct_cache(
                    cache=cache, base_path=DATA_PATH, deduce_version="2.5.0"
                )

    def test_validate_lookup_struct_cache_file_changes(self):

        cache = {
            "deduce_version": "2.5.0",
            "saved_datetime": "2023-12-06 10:19:39.198133",
            "lookup_structs": "_",
        }

        class MockStats:
            st_mtime = 2000000000  # way in the future

        with patch("pathlib.Path.glob", return_value=[1, 2, 3]):
            with patch("os.stat", return_value=MockStats()):
                assert not validate_lookup_struct_cache(
                    cache=cache, base_path=DATA_PATH, deduce_version="2.5.0"
                )

    @patch("deduce.lookup_structs.validate_lookup_struct_cache", return_value=True)
    @pytest.mark.skip("Temporeraly disabled because unable to untangle all the dependencies on the cache file")
    def test_load_lookup_structs_from_cache(self, _):
       
        ds_collection = load_lookup_structs_from_cache(
            base_path=DATA_PATH, deduce_version="_"
        )

        assert len(ds_collection) == 4
        assert "test" in ds_collection
        assert "test_nested" in ds_collection
        assert "prefix" in ds_collection.keys()
        assert "street" in ds_collection.keys()

    @patch("deduce.lookup_structs.validate_lookup_struct_cache", return_value=True)
    def test_load_lookup_structs_from_cache_nofile(self, _):

        ds_collection = load_lookup_structs_from_cache(
            base_path=DATA_PATH / "non_existing_dir", deduce_version="_"
        )

        assert ds_collection is None

    @patch("deduce.lookup_structs.validate_lookup_struct_cache", return_value=False)
    def test_load_lookup_structs_from_cache_invalid(self, _):

        ds_collection = load_lookup_structs_from_cache(
            base_path=DATA_PATH, deduce_version="_"
        )

        assert ds_collection is None

    @patch("builtins.open", return_value=io.BytesIO())
    @patch("pickle.dump")
    def test_cache_lookup_structs(self, _, mock_pickle_dump):

        cache_lookup_structs(
            lookup_structs=dd.ds.DsCollection(),
            base_path=DATA_PATH,
            deduce_version="2.5.0",
        )

        assert mock_pickle_dump.called_once()
