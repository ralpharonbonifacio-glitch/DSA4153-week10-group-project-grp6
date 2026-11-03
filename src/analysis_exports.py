"""
Analysis Export Module

This module handles exporting analytical results.
"""

import pandas as pd

def export_analysis_results(results, output_path):
    """
    Exports analysis results to a CSV file.

    Parameters:
        results (DataFrame): The analysis results.
        output_path (str): The destination file path.

    Returns:
        bool: True if the export is successful.
    """

    results.to_csv(output_path, index=False)

    return True