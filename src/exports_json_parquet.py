import pandas as pd

def export_to_json(data: pd.DataFrame, output_path: str) -> bool:
    """
    exports a DataFrame to JSON format using 'records' orientation to drop incidental indexes.
    """
    try:
        data.to_json(output_path, orient='records', indent=4, force_ascii=False)
        return True
    except Exception as e:
        print(f"Error exporting JSON to {output_path}: {e}")
        return False

def export_to_parquet(data: pd.DataFrame, output_path: str) -> bool:
    """
    exports a DataFrame to Parquet format using the PyArrow engine.
    """
    try:
        data.to_parquet(output_path, engine='pyarrow', index=False)
        return True
    except Exception as e:
        print(f"Error exporting Parquet to {output_path}: {e}")
        return False