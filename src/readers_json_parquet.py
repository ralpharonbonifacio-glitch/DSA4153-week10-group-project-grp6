import json
import pandas as pd
import pyarrow.parquet as pq
from typing import Dict, Any

CANONICAL_COLUMNS = ['country', 'continent', 'year', 'lifeExp', 'pop', 'gdpPercap']

def read_json_file(file_path: str, manifest: Dict[str, Any]) -> pd.DataFrame:
    """
    reads and flattens nested JSON records into a pandas DataFrame.
    maps columns to canonical names and raises errors for missing required columns.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # bypass the outer metadata object to find the nested list of records
    records = None
    for key, value in data.items():
        if isinstance(value, list):
            records = value
            break
            
    if records is None:
        raise ValueError(f"File-level error: No nested record list found in JSON {file_path}")

    df = pd.json_normalize(records)

    # map columns based on manifest rules
    mapping = manifest.get('file_mappings', {}).get('json', {})
    if mapping:
        df = df.rename(columns=mapping)

    # reject missing required columns as a file-level error
    missing = set(CANONICAL_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"File-level error: Missing required canonical columns in JSON: {missing}")

    return df[CANONICAL_COLUMNS]

def read_parquet_file(file_path: str, manifest: Dict[str, Any]) -> pd.DataFrame:
    """
    reads Parquet records using PyArrow into a pandas DataFrame.
    maps columns and returns raw strings for validation prior to casting.
    """
    # use PyArrow to read the Parquet file as specified
    table = pq.read_table(file_path)
    df = table.to_pandas()

    mapping = manifest.get('file_mappings', {}).get('parquet', {})
    if mapping:
        df = df.rename(columns=mapping)

    missing = set(CANONICAL_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"File-level error: Missing required canonical columns in Parquet: {missing}")

    return df[CANONICAL_COLUMNS]