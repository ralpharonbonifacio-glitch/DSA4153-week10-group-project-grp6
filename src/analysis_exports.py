
"""
Analysis Export Module

This module handles exporting analytical results.
"""

from pathlib import Path

import pandas as pd


def export_analysis_results(
    results: pd.DataFrame,
    output_path: str | Path
) -> bool:
    """
    Exports analysis results to a CSV file.

    Parameters:
        results (DataFrame): The analysis results.
        output_path (str or Path): The destination file path.

    Returns:
        bool: True if the export is successful.

    Raises:
        TypeError: If results is not a DataFrame.
    """

    if not isinstance(results, pd.DataFrame):
        raise TypeError("Results must be a pandas DataFrame.")

    results.to_csv(output_path, index=False)

    return True