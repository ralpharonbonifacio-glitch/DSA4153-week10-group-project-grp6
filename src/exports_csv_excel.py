
"""Export functions for CSV and Excel files."""

from pathlib import Path
import pandas as pd


def export_to_csv(data, output_path):
    """Export a pandas DataFrame to a CSV file."""
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Data must be a pandas DataFrame.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data.to_csv(
        output_path,
        index=False,
        encoding="cp1252",
        sep=";"
    )

    return str(output_path)


def export_to_excel(data, output_path):
    """Export a pandas DataFrame to an Excel file."""
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Data must be a pandas DataFrame.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data.to_excel(
        output_path,
        sheet_name="observations",
        index=False,
        engine="openpyxl"
    )

    return str(output_path)
