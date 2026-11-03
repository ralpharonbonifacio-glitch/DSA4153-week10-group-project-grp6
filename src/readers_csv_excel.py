"""Readers for CSV and Excel input files."""

from pathlib import Path
import pandas as pd


def _get_file_config(manifest, file_format):
    """Get the configuration for a file format from the manifest."""
    for file_config in manifest["files"]:
        if file_config["format"] == file_format:
            return file_config

    raise ValueError(f"No {file_format} configuration found in manifest.")


def _standardize_data(data, file_config, manifest):
    """Rename columns and arrange data using the canonical schema."""
    ignore_columns = file_config.get("ignore_columns", [])
    data = data.drop(columns=ignore_columns, errors="ignore")

    data = data.rename(columns=file_config["source_to_canonical"])

    canonical_columns = manifest["canonical_order"]

    missing_columns = [
        column for column in canonical_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    data = data[canonical_columns].copy()

    for column, data_type in manifest["canonical_schema"].items():
        if data_type == "string":
            data[column] = data[column].astype("string").str.strip()

        elif data_type in ("int64", "float64"):
            numeric_data = pd.to_numeric(data[column], errors="coerce")

            if data_type == "int64":
                valid_numbers = numeric_data.dropna()

                if (valid_numbers % 1 == 0).all():
                    data[column] = numeric_data.astype("Int64")
                else:
                    data[column] = numeric_data
            else:
                data[column] = numeric_data.astype("float64")

    return data


def read_csv_file(file_path, manifest):
    """Read a CSV file and return a canonical pandas DataFrame."""
    file_config = _get_file_config(manifest, "csv")

    if not Path(file_path).is_file():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    data = pd.read_csv(
        file_path,
        encoding=file_config.get("encoding", "utf-8"),
        sep=file_config.get("separator", ","),
        comment=file_config.get("comment_prefix"),
    )

    return _standardize_data(data, file_config, manifest)


def read_excel_file(file_path, manifest):
    """Read an Excel file and return a canonical pandas DataFrame."""
    file_config = _get_file_config(manifest, "xlsx")

    if not Path(file_path).is_file():
        raise FileNotFoundError(f"Excel file not found: {file_path}")

    data = pd.read_excel(
        file_path,
        sheet_name=file_config.get("sheet_name", 0),
        engine=file_config.get("engine", "openpyxl"),
    )

    return _standardize_data(data, file_config, manifest)