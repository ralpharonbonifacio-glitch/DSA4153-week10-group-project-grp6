"""Tests for src/validation.py and src/reconciliation.py (Member 3)."""
 
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
        ["A", "Asia", 1952, 150.0, 100, 700.0],   # lifeExp too high
        ["B", "Asia", 1952, -5.0, 100, 700.0],    # lifeExp negative
        ["C", "Asia", 1952, 50.0, -1, 700.0],     # negative population
        ["D", "Asia", 1952, 50.0, 100, -10.0],    # negative gdp
        ["E", "Asia", 1500, 50.0, 100, 700.0],    # year too early
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
    assert "pop: must be greater than 0" in reason
 
 
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
 
 
def test_boundary_values_follow_manifest_rules():
    df = make_df([
        ["A", "Asia", 1952, 120.0, 1, 0.01],   # lifeExp exactly 120 is allowed
        ["B", "Asia", 1952, 120.1, 1, 1.0],    # above 120
        ["C", "Asia", 1952, 0.0, 1, 1.0],      # lifeExp must be greater than 0
        ["D", "Asia", 1952, 50.0, 0, 1.0],     # pop must be greater than 0
        ["E", "Asia", 1952, 50.0, 1, 0.0],     # gdpPercap must be greater than 0
    ])
    result = validate_data(df)
    assert result["valid"]["country"].tolist() == ["A"]
    assert len(result["rejected"]) == 4
 
 
def test_year_must_be_in_allowed_years():
    df = make_df([
        ["A", "Asia", 2007, 50.0, 100, 700.0],
        ["B", "Asia", 1953, 50.0, 100, 700.0],   # not a 5-year step
        ["C", "Asia", 2012, 50.0, 100, 700.0],   # outside the range
    ])
    result = validate_data(df)
    assert result["valid"]["country"].tolist() == ["A"]
    assert "year: not an allowed value" in result["rejected"]["reject_reason"].iloc[0]
 
 
def test_non_finite_values_are_rejected():
    df = make_df([["A", "Asia", 2007, float("inf"), 100, 700.0]])
    assert not validate_data(df)["rejected"].empty
 
 
def test_load_rules_reads_allowed_lists_from_manifest():
    manifest = {"allowed_continents": ["Asia"], "allowed_years": [2020]}
    rules = load_rules(manifest)
    df = make_df([
        ["A", "Asia", 2020, 50.0, 100, 700.0],
        ["B", "Europe", 2020, 50.0, 100, 700.0],
        ["C", "Asia", 2007, 50.0, 100, 700.0],
    ])
    assert validate_data(df, rules)["valid"]["country"].tolist() == ["A"]
    assert len(validate_data(df)["valid"]) == 1  # default rules allow only 1952-2007
 
 
def test_validation_rules_section_can_override():
    rules = load_rules({"validation_rules": {"lifeExp": {"max": 90}}})
    df = make_df([["A", "Asia", 2007, 95.0, 100, 700.0]])
    assert validate_data(df, rules)["valid"].empty
 
 
def test_accepts_nullable_dtypes_from_csv_reader():
    """Member 1's reader returns string and nullable Int64 columns."""
    df = pd.DataFrame({
        "country": pd.array(["A", "B", None], dtype="string"),
        "continent": pd.array(["Asia", "Asia", "Asia"], dtype="string"),
        "year": pd.array([2002, None, 2007], dtype="Int64"),
        "lifeExp": [60.0, 61.0, float("nan")],
        "pop": pd.array([100, 200, None], dtype="Int64"),
        "gdpPercap": [1.0, 2.0, 3.0],
    })
    result = validate_data(df)
    assert result["valid"]["country"].tolist() == ["A"]
    assert result["valid"]["year"].dtype == "int64"
    assert len(result["rejected"]) == 2
 
 
def test_accepts_all_text_columns_from_parquet_reader():
    """Member 2's Parquet reader returns every value as a string."""
    df = make_df([["Philippines", "Asia", "2007", "71.688", "91077287", "3190.481016"]])
    result = validate_data(df)
    assert len(result["valid"]) == 1
    assert result["valid"]["pop"].iloc[0] == 91077287
 
 
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
 
 
# ---------- reconcile_data ----------
 
def test_reconcile_same_data_from_two_formats():
    result = reconcile_data({"csv": make_df(good_rows()), "json": make_df(good_rows())})
    assert len(result["clean"]) == 3
    assert result["summary"]["duplicate_records_removed"] == 3
    assert result["summary"]["conflicting_keys"] == 0
    assert list(result["clean"].columns) == CANONICAL_COLUMNS
 
 
def test_reconcile_quarantines_conflicts_and_rejects_invalid():
    csv_rows = good_rows() + [["Bad", "Asia", 1952, 999.0, 100, 700.0]]
    json_rows = [["Afghanistan", "Asia", 1952, 35.0, 8425333, 779.4453]]  # conflicts with csv
    result = reconcile_data({"csv": make_df(csv_rows), "json": make_df(json_rows)})
 
    assert len(result["rejected"]) == 1
    assert result["rejected"]["source"].iloc[0] == "csv"
    assert result["summary"]["conflicting_keys"] == 1
    assert set(result["conflicts"]["source"]) == {"csv", "json"}
    # Afghanistan 1952 is quarantined, the other 2 good rows stay
    assert len(result["clean"]) == 2
    assert not ((result["clean"]["country"] == "Afghanistan") & (result["clean"]["year"] == 1952)).any()
 
 
def test_reconcile_accepts_list_of_dataframes():
    result = reconcile_data([make_df(good_rows()), make_df(good_rows())])
    assert result["summary"]["sources"] == ["source_1", "source_2"]
    assert len(result["clean"]) == 3
 
 
def test_reconcile_rejects_empty_input():
    with pytest.raises(ValueError):
        reconcile_data([])
 
 
def test_reconcile_rejects_wrong_type():
    with pytest.raises(TypeError):
        reconcile_data({"csv": "not a dataframe"})
 
 
def test_reconcile_clean_data_is_sorted():
    rows = list(reversed(good_rows()))
    clean = reconcile_data({"csv": make_df(rows)})["clean"]
    assert clean["country"].tolist() == ["Afghanistan", "Afghanistan", "Albania"]
    assert clean["year"].tolist() == [1952, 1957, 1952]
 
 
# ---------- generate_validation_report ----------
 
def build_results():
    csv_rows = good_rows() + [["Bad", "Asia", 1952, 999.0, 100, 700.0]]
    json_rows = [["Afghanistan", "Asia", 1952, 35.0, 8425333, 779.4453]]
    return reconcile_data({"csv": make_df(csv_rows), "json": make_df(json_rows)})
 
 
def test_report_json_can_be_read_back(tmp_path):
    output_path = tmp_path / "reports" / "report.json"
    generate_validation_report(build_results(), output_path)
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["summary"]["rejected_records"] == 1
    assert len(report["rejected_records"]) == 1
    assert len(report["conflicting_records"]) == 2
 
 
def test_report_text_contains_key_sections(tmp_path):
    output_path = tmp_path / "report.txt"
    returned = generate_validation_report(build_results(), output_path)
    text = output_path.read_text(encoding="utf-8")
    assert returned == str(output_path)
    assert "VALIDATION REPORT" in text
    assert "REJECTED RECORDS" in text
    assert "CONFLICTING RECORDS" in text
    assert "lifeExp: above maximum" in text
 
 
def test_report_rejects_invalid_results(tmp_path):
    with pytest.raises(ValueError):
        generate_validation_report({"oops": 1}, tmp_path / "report.txt")
 
 
# ---------- expected counts from manifest.json ----------
 
def build_manifest_sized_file():
    """One file shaped like the manifest says: 1712 raw rows, 6 invalid, 2 duplicates."""
    years = [1952, 1957, 1962, 1967, 1972, 1977, 1982, 1987, 1992, 1997, 2002, 2007]
    rows = [
        [f"Country{index}", "Asia", year, 50.0 + index / 10, 1000 + index, 500.0 + year]
        for index in range(142)
        for year in years
    ]
    assert len(rows) == 1704
    rows += rows[:2]                                       # 2 exact duplicates
    rows += [
        ["", "Asia", 2007, 50.0, 100, 500.0],              # empty country
        ["X1", "Atlantica", 2007, 50.0, 100, 500.0],       # unsupported continent
        ["X2", "Asia", 1999, 50.0, 100, 500.0],            # year not allowed
        ["X3", "Asia", 2007, 130.0, 100, 500.0],           # lifeExp too high
        ["X4", "Asia", 2007, 50.0, 0, 500.0],              # pop is zero
        ["X5", "Asia", 2007, 50.0, 100, -1.0],             # negative gdp
    ]
    return make_df(rows)
 
 
def test_single_file_matches_manifest_expected_counts():
    result = reconcile_data({"csv": build_manifest_sized_file()})
    summary = result["summary"]
    assert summary["total_input_records"] == 1712
    assert summary["rejected_records"] == 6
    assert summary["per_source"]["csv"]["valid_records"] == 1706
    assert summary["duplicate_records_removed"] == 2
    assert summary["clean_records"] == 1704
    assert summary["conflicting_keys"] == 0
 
 
def test_four_identical_files_give_the_same_clean_data():
    df = build_manifest_sized_file()
    sources = {"csv": df, "xlsx": df.copy(), "json": df.copy(), "parquet": df.copy()}
    result = reconcile_data(sources)
    assert result["summary"]["clean_records"] == 1704
    assert result["summary"]["rejected_records"] == 24
    assert result["summary"]["conflicting_keys"] == 0