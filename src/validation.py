"""
Validation and duplicate / conflict detection (Member 3).

All functions work on pandas DataFrames that use the canonical columns:
country, continent, year, lifeExp, pop, gdpPercap
"""

from collections import Counter

import numpy as np
import pandas as pd

CANONICAL_COLUMNS = ["country", "continent", "year", "lifeExp", "pop", "gdpPercap"]
KEY_COLUMNS = ["country", "year"]
TEXT_COLUMNS = ["country", "continent"]
NUMERIC_COLUMNS = ["year", "lifeExp", "pop", "gdpPercap"]
INTEGER_COLUMNS = ["year", "pop"]

# Fallback rules used when manifest.json does not provide "validation_rules".
# Keep these in sync with data/manifest.json.
DEFAULT_RULES = {
    "allowed_continents": ["Africa", "Americas", "Asia", "Europe", "Oceania"],
    "year": {"min": 1800, "max": 2100},
    "lifeExp": {"min": 0, "max": 125},
    "pop": {"min": 0},
    "gdpPercap": {"min": 0},
}


def load_rules(manifest=None):
    """Build the validation rules from a manifest dict (or use the defaults).

    The manifest may contain a "validation_rules" section that uses the same
    structure as DEFAULT_RULES. Missing parts fall back to the defaults.
    """
    rules = {key: (dict(value) if isinstance(value, dict) else list(value))
             for key, value in DEFAULT_RULES.items()}
    manifest_rules = (manifest or {}).get("validation_rules", {})
    for key, value in manifest_rules.items():
        if isinstance(value, dict) and isinstance(rules.get(key), dict):
            rules[key].update(value)
        else:
            rules[key] = value
    return rules

def _check_input(data):
    """Raise a clear error if data is not a DataFrame with all canonical columns."""
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")
    missing = [col for col in CANONICAL_COLUMNS if col not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _blank_mask(series):
    """True where a value is missing (NaN/None) or an empty / whitespace string."""
    return series.isna() | series.astype(str).str.strip().eq("")


def validate_data(data, rules=None):
    """Check every record against the validation rules.

    Parameters
    ----------
    data : pandas DataFrame with the six canonical columns.
    rules : optional dict (see DEFAULT_RULES). Use load_rules(manifest) to build it.

    Returns
    -------
    dict with:
        "valid"    - DataFrame, canonical columns only, with the correct dtypes
        "rejected" - DataFrame, original columns + "reject_reason"
        "summary"  - dict with record counts and a count per reject reason
    """
    _check_input(data)
    rules = rules if rules is not None else load_rules()
    df = data.copy()
    reasons = [[] for _ in range(len(df))]

    def flag(mask, message):
        for position in np.flatnonzero(np.asarray(mask)):
            reasons[position].append(message)

    for col in TEXT_COLUMNS:
        flag(_blank_mask(df[col]), f"{col}: missing value")

    allowed = rules.get("allowed_continents")
    if allowed:
        continent_text = df["continent"].astype(str).str.strip()
        unsupported = ~_blank_mask(df["continent"]) & ~continent_text.isin(allowed)
        flag(unsupported, "continent: unsupported value")

    numeric_values = {}
    for col in NUMERIC_COLUMNS:
        blank = _blank_mask(df[col])
        numbers = pd.to_numeric(df[col], errors="coerce")
        numbers = numbers.replace([np.inf, -np.inf], np.nan)
        numeric_values[col] = numbers

        flag(blank, f"{col}: missing value")
        flag(~blank & numbers.isna(), f"{col}: not a valid number")

        has_number = numbers.notna()
        if col in INTEGER_COLUMNS:
            flag(has_number & (numbers % 1 != 0), f"{col}: must be a whole number")

        col_rules = rules.get(col, {})
        if "min" in col_rules:
            flag(has_number & (numbers < col_rules["min"]),
                 f"{col}: below minimum {col_rules['min']}")
        if "max" in col_rules:
            flag(has_number & (numbers > col_rules["max"]),
                 f"{col}: above maximum {col_rules['max']}")

    is_valid = np.array([len(item) == 0 for item in reasons], dtype=bool)

    valid = df.loc[is_valid, CANONICAL_COLUMNS].copy()
    for col in TEXT_COLUMNS:
        valid[col] = valid[col].astype(str).str.strip()
    for col in NUMERIC_COLUMNS:
        values = numeric_values[col][is_valid]
        valid[col] = values.astype("int64") if col in INTEGER_COLUMNS else values.astype("float64")

    rejected = df.loc[~is_valid].copy()
    rejected["reject_reason"] = [
        "; ".join(item) for item, ok in zip(reasons, is_valid) if not ok
    ]

    reason_counts = Counter(
        message for item in reasons for message in item
    )
    summary = {
        "total_records": int(len(df)),
        "valid_records": int(is_valid.sum()),
        "rejected_records": int((~is_valid).sum()),
        "reject_reasons": dict(reason_counts),
    }
    return {"valid": valid, "rejected": rejected, "summary": summary}

def remove_duplicates(data):
    """Remove exact duplicate records (all six canonical columns are equal).

    The first occurrence is kept.

    Returns
    -------
    (unique_records, removed_duplicates) - both DataFrames
    """
    _check_input(data)
    is_duplicate = data.duplicated(subset=CANONICAL_COLUMNS, keep="first")
    return data[~is_duplicate].copy(), data[is_duplicate].copy()


def detect_conflicts(data):
    """Find (country, year) keys that appear with different values.

    Exact duplicates are not conflicts, so they are ignored here.

    Returns
    -------
    DataFrame with every record that belongs to a conflicting key, sorted by
    country and year. Empty DataFrame (same columns) if there are no conflicts.
    """
    _check_input(data)
    unique_records = data.drop_duplicates(subset=CANONICAL_COLUMNS, keep="first")
    in_conflict = unique_records.duplicated(subset=KEY_COLUMNS, keep=False)
    conflicts = unique_records[in_conflict]
    return conflicts.sort_values(KEY_COLUMNS, kind="stable").copy()