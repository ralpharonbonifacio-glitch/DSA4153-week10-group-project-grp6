import json
from pathlib import Path
 
import pandas as pd
import pyarrow.parquet as pq
 
 
def _get_file_config(manifest, file_format):
    """Get the configuration for a file format from the manifest."""
    for file_config in manifest["files"]:
        if file_config["format"] == file_format:
            return file_config
 
    raise ValueError(f"No {file_format} configuration found in manifest.")
 
 
def _to_canonical(data, file_config, manifest):
    """Rename columns to canonical names and return them in canonical order."""
    data = data.rename(columns=file_config["source_to_canonical"])
    canonical_columns = manifest["canonical_order"]
 
    missing_columns = [
        column for column in canonical_columns
        if column not in data.columns
    ]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
 
    return data[canonical_columns].copy()
 
 
def read_json_file(file_path, manifest):
    """Read a JSON file, flatten its records and return a canonical DataFrame.
 
    Values are returned as they appear in the file. Type conversion and
    validation are done later by src/validation.py.
    """
    file_config = _get_file_config(manifest, "json")
 
    if not Path(file_path).is_file():
        raise FileNotFoundError(f"JSON file not found: {file_path}")
 
    with open(file_path, "r", encoding=file_config.get("encoding", "utf-8")) as file:
        content = json.load(file)
 
    # the manifest says where the records are (the "metadata" object is not a record)
    record_path = file_config.get("record_path")
    if record_path:
        if not isinstance(content, dict) or record_path not in content:
            raise ValueError(f"Record list '{record_path}' not found in {file_path}")
        records = content[record_path]
    else:
        records = content
 
    if not isinstance(records, list):
        raise ValueError(f"No list of records found in {file_path}")
 
    # flattens identity.country, measures.lifeExp, ... into separate columns
    data = pd.json_normalize(records)
 
    return _to_canonical(data, file_config, manifest)
 
 
def read_parquet_file(file_path, manifest):
    """Read a Parquet file with PyArrow and return a canonical DataFrame.
 
    The input columns are stored as strings, so they are returned unchanged.
    Type conversion and validation are done later by src/validation.py.
    """
    file_config = _get_file_config(manifest, "parquet")
 
    if not Path(file_path).is_file():
        raise FileNotFoundError(f"Parquet file not found: {file_path}")
 
    data = pq.read_table(file_path).to_pandas()
 
    return _to_canonical(data, file_config, manifest)