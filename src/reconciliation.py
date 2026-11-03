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

REPORT_SAMPLE_ROWS = 20  # rows shown per table in the text report


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