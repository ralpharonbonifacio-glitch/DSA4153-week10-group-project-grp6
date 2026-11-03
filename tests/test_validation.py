"""
Tests for src/validation.py and src/reconciliation.py (Member 3).
"""

import json

import pandas as pd
import pytest

from src.reconciliation import generate_validation_report, reconcile_data
from src.validation import (
    CANONICAL_COLUMNS,
    detect_conflicts,
    load_rules,
    remove_duplicates,
    validate_data,
)


def make_df(rows):
    return pd.DataFrame(rows, columns=CANONICAL_COLUMNS)


def good_rows():
    return [
        ["Afghanistan", "Asia", 1952, 28.801, 8425333, 779.4453],
        ["Afghanistan", "Asia", 1957, 30.332, 9240934, 820.8530],
        ["Albania", "Europe", 1952, 55.230, 1282697, 1601.0561],
    ]


# ---------- validate_data ----------

def test_valid_records_pass_with_correct_dtypes():
    result = validate_data(make_df(good_rows()))
    assert len(result["valid"]) == 3
    assert result["rejected"].empty
    assert list(result["valid"].columns) == CANONICAL_COLUMNS
    assert result["valid"]["year"].dtype == "int64"
    assert result["valid"]["pop"].dtype == "int64"
    assert result["valid"]["lifeExp"].dtype == "float64"
    assert result["valid"]["gdpPercap"].dtype == "float64"
    assert result["summary"]["valid_records"] == 3


def test_numbers_stored_as_text_are_converted():
    df = make_df([["Albania", "Europe", "1952", "55.23", "1282697", "1601.05"]])
    result = validate_data(df)
    assert len(result["valid"]) == 1
    assert result["valid"]["year"].iloc[0] == 1952


def test_missing_values_are_rejected():
    df = make_df([
        [None, "Asia", 1952, 28.8, 100, 700.0],
        ["Albania", "", 1952, 55.2, 100, 1600.0],
        ["Algeria", "Africa", None, 43.0, 100, 2449.0],
        ["Angola", "Africa", 1952, float("nan"), 100, 3520.0],
    ])
    result = validate_data(df)
    assert result["valid"].empty
    assert len(result["rejected"]) == 4
    reasons = result["rejected"]["reject_reason"].tolist()
    assert "country: missing value" in reasons[0]
    assert "continent: missing value" in reasons[1]
    assert "year: missing value" in reasons[2]
    assert "lifeExp: missing value" in reasons[3]


def test_non_numeric_values_are_rejected():
    df = make_df([["Albania", "Europe", 1952, "abc", 1282697, 1601.0]])
    result = validate_data(df)
    assert "lifeExp: not a valid number" in result["rejected"]["reject_reason"].iloc[0]


def test_out_of_range_values_are_rejected():
    df = make_df([
        ["A", "Asia", 1952, 150.0, 100, 700.0],
        ["B", "Asia", 1952, -5.0, 100, 700.0],
        ["C", "Asia", 1952, 50.0, -1, 700.0],
        ["D", "Asia", 1952, 50.0, 100, -10.0],
        ["E", "Asia", 1500, 50.0, 100, 700.0],
    ])
    result = validate_data(df)
    assert result["valid"].empty
    assert len(result["rejected"]) == 5

def test_fractional_year_and_population_are_rejected():
    df = make_df([
        ["A", "Asia", 1952.5, 50.0, 100, 700.0],
        ["B", "Asia", 1952, 50.0, 100.5, 700.0],
    ])
    result = validate_data(df)
    reasons = result["rejected"]["reject_reason"].tolist()
    assert "year: must be a whole number" in reasons[0]
    assert "pop: must be a whole number" in reasons[1]


def test_unsupported_continent_is_rejected():
    df = make_df([["Atlantis", "Atlantica", 1952, 50.0, 100, 700.0]])
    result = validate_data(df)
    assert "continent: unsupported value" in result["rejected"]["reject_reason"].iloc[0]


def test_multiple_problems_in_one_record_are_all_reported():
    df = make_df([["", "Asia", 1952, 500.0, -1, 700.0]])
    reason = validate_data(df)["rejected"]["reject_reason"].iloc[0]
    assert "country: missing value" in reason
    assert "lifeExp: above maximum" in reason
    assert "pop: below minimum" in reason


def test_valid_and_invalid_are_split_correctly():
    rows = good_rows() + [["Bad", "Asia", 1952, 999.0, 100, 700.0]]
    result = validate_data(make_df(rows))
    assert len(result["valid"]) == 3
    assert len(result["rejected"]) == 1
    assert result["summary"]["total_records"] == 4


def test_missing_column_raises_value_error():
    with pytest.raises(ValueError):
        validate_data(make_df(good_rows()).drop(columns=["pop"]))


def test_non_dataframe_raises_type_error():
    with pytest.raises(TypeError):
        validate_data([1, 2, 3])


def test_original_data_is_not_modified():
    df = make_df(good_rows())
    before = df.copy()
    validate_data(df)
    pd.testing.assert_frame_equal(df, before)


def test_custom_rules_from_manifest():
    manifest = {"validation_rules": {"year": {"min": 1952, "max": 2007}}}
    rules = load_rules(manifest)
    df = make_df([["A", "Asia", 2020, 50.0, 100, 700.0]])
    assert validate_data(df, rules)["valid"].empty
    assert len(validate_data(df)["valid"]) == 1


# ---------- remove_duplicates ----------

def test_remove_duplicates_removes_exact_copies():
    rows = good_rows() + [good_rows()[0]]
    unique, removed = remove_duplicates(make_df(rows))
    assert len(unique) == 3
    assert len(removed) == 1


def test_remove_duplicates_keeps_different_values_for_same_key():
    rows = good_rows() + [["Afghanistan", "Asia", 1952, 99.0, 8425333, 779.4453]]
    unique, removed = remove_duplicates(make_df(rows))
    assert len(unique) == 4
    assert removed.empty


def test_remove_duplicates_without_duplicates():
    unique, removed = remove_duplicates(make_df(good_rows()))
    assert len(unique) == 3
    assert removed.empty


# ---------- detect_conflicts ----------

def test_detect_conflicts_finds_same_key_with_different_values():
    rows = good_rows() + [["Afghanistan", "Asia", 1952, 35.0, 8425333, 779.4453]]
    conflicts = detect_conflicts(make_df(rows))
    assert len(conflicts) == 2
    assert set(conflicts["country"]) == {"Afghanistan"}
    assert set(conflicts["year"]) == {1952}


def test_detect_conflicts_ignores_exact_duplicates():
    rows = good_rows() + [good_rows()[0]]
    assert detect_conflicts(make_df(rows)).empty


def test_detect_conflicts_none():
    conflicts = detect_conflicts(make_df(good_rows()))
    assert conflicts.empty
    assert list(conflicts.columns) == CANONICAL_COLUMNS
