"""
Reconciliation of data from different file formats and validation reports (Member 3).
"""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.validation import (
    CANONICAL_COLUMNS,
    KEY_COLUMNS,
    detect_conflicts,
    remove_duplicates,
    validate_data,
)

REPORT_SAMPLE_ROWS = 20  


def _name_sources(dataframes):
    """Accept a dict {source_name: DataFrame} or a list of DataFrames."""
    if isinstance(dataframes, dict):
        items = list(dataframes.items())
    elif isinstance(dataframes, (list, tuple)):
        items = [(f"source_{index + 1}", df) for index, df in enumerate(dataframes)]
    else:
        raise TypeError("dataframes must be a dict {name: DataFrame} or a list of DataFrames")

    if not items:
        raise ValueError("No dataframes were provided")
    for name, df in items:
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Source '{name}' is not a pandas DataFrame")
    return items

def reconcile_data(dataframes, rules=None):
    """Combine data from different formats into one clean dataset.

    Steps:
      1. Validate each source; invalid records are rejected.
      2. Combine the valid records.
      3. Remove exact duplicates (the same record in several formats is normal).
      4. Detect conflicting (country, year) keys. Conflicting records are
         quarantined: they are removed from the clean data and reported.

    Parameters
    ----------
    dataframes : dict {source_name: DataFrame} or list of DataFrames.
    rules : optional validation rules (see validation.load_rules).

    Returns
    -------
    dict with:
        "clean"      - DataFrame, canonical columns only, sorted by country, year
        "rejected"   - DataFrame, invalid records + "source" + "reject_reason"
        "duplicates" - DataFrame, removed exact duplicates (+ "source")
        "conflicts"  - DataFrame, records with conflicting keys (+ "source")
        "summary"    - dict with counts (overall and per source)
    """
    sources = _name_sources(dataframes)

    valid_parts, rejected_parts, per_source = [], [], {}
    for name, df in sources:
        result = validate_data(df, rules)
        valid = result["valid"].copy()
        valid["source"] = name
        rejected = result["rejected"].copy()
        rejected["source"] = name
        valid_parts.append(valid)
        rejected_parts.append(rejected)
        per_source[name] = result["summary"]

    combined = pd.concat(valid_parts, ignore_index=True)
    rejected_all = pd.concat(rejected_parts, ignore_index=True)

    unique_records, duplicates = remove_duplicates(combined)
    conflicts = detect_conflicts(unique_records)

    if conflicts.empty:
        clean = unique_records
    else:
        conflict_keys = conflicts[KEY_COLUMNS].drop_duplicates()
        marked = unique_records.merge(conflict_keys, on=KEY_COLUMNS, how="left", indicator=True)
        clean = marked[marked["_merge"] == "left_only"].drop(columns="_merge")

    clean = (
        clean[CANONICAL_COLUMNS]
        .sort_values(KEY_COLUMNS, kind="stable")
        .reset_index(drop=True)
    )

    summary = {
        "sources": list(per_source.keys()),
        "per_source": per_source,
        "total_input_records": sum(s["total_records"] for s in per_source.values()),
        "rejected_records": int(len(rejected_all)),
        "duplicate_records_removed": int(len(duplicates)),
        "conflicting_keys": int(len(conflicts[KEY_COLUMNS].drop_duplicates())) if not conflicts.empty else 0,
        "conflicting_records": int(len(conflicts)),
        "clean_records": int(len(clean)),
    }
    return {
        "clean": clean,
        "rejected": rejected_all,
        "duplicates": duplicates.reset_index(drop=True),
        "conflicts": conflicts.reset_index(drop=True),
        "summary": summary,
    }

def _table_to_text(df):
    if df is None or len(df) == 0:
        return "  (none)\n"
    text = df.head(REPORT_SAMPLE_ROWS).to_string(index=False)
    text = "\n".join("  " + line for line in text.splitlines())
    if len(df) > REPORT_SAMPLE_ROWS:
        text += f"\n  ... and {len(df) - REPORT_SAMPLE_ROWS} more"
    return text + "\n"


def generate_validation_report(results, output_path):
    """Write the validation / audit report for a reconcile_data() result.

    The format depends on the file extension:
      .json -> full machine-readable report (all rejected, duplicate and conflict records)
      other -> readable text report (first rows of each table)

    Returns the output path as a string once the report has been written.
    """
    required = {"summary", "rejected", "duplicates", "conflicts"}
    if not isinstance(results, dict) or not required.issubset(results):
        raise ValueError(f"results must be a reconcile_data() result containing {sorted(required)}")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now().isoformat(timespec="seconds")
    summary = results["summary"]

    if output_path.suffix.lower() == ".json":
        report = {
            "generated_at": generated_at,
            "summary": summary,
            "rejected_records": json.loads(results["rejected"].to_json(orient="records")),
            "duplicate_records": json.loads(results["duplicates"].to_json(orient="records")),
            "conflicting_records": json.loads(results["conflicts"].to_json(orient="records")),
        }
        output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return str(output_path)

    lines = [
        "VALIDATION REPORT",
        f"Generated: {generated_at}",
        "",
        "SUMMARY",
        f"  Sources: {', '.join(summary['sources'])}",
        f"  Total input records:       {summary['total_input_records']}",
        f"  Rejected (invalid):        {summary['rejected_records']}",
        f"  Exact duplicates removed:  {summary['duplicate_records_removed']}",
        f"  Conflicting keys:          {summary['conflicting_keys']}"
        f" ({summary['conflicting_records']} records quarantined)",
        f"  Clean records:             {summary['clean_records']}",
        "",
        "PER SOURCE",
    ]
    for name, info in summary["per_source"].items():
        lines.append(
            f"  {name}: {info['total_records']} total, "
            f"{info['valid_records']} valid, {info['rejected_records']} rejected"
        )
        for reason, count in info["reject_reasons"].items():
            lines.append(f"      {reason}: {count}")
    lines += [
        "",
        "REJECTED RECORDS",
        _table_to_text(results["rejected"]),
        "CONFLICTING RECORDS (same country and year, different values)",
        _table_to_text(results["conflicts"]),
        "EXACT DUPLICATES REMOVED",
        _table_to_text(results["duplicates"]),
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return str(output_path)
