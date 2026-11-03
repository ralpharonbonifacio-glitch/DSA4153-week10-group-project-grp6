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

    