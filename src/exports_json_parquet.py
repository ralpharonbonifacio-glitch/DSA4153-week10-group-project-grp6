from pathlib import Path
 
import pandas as pd
 
 
def export_to_json(data, output_path):
    """Export a pandas DataFrame to a JSON file (a list of records)."""
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Data must be a pandas DataFrame.")
 
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
 
    data.to_json(output_path, orient="records", indent=4, force_ascii=False)
 
    return str(output_path)
 
 
def export_to_parquet(data, output_path):
    """Export a pandas DataFrame to a Parquet file using PyArrow."""
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Data must be a pandas DataFrame.")
 
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
 
    data.to_parquet(output_path, engine="pyarrow", index=False)
 
    return str(output_path)