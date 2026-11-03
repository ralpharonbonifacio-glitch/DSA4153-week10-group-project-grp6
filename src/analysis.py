"""
Data Analysis Module

This module contains functions for analyzing
country-level data using pandas and NumPy.
"""

import pandas as pd
import numpy as np

def generate_descriptive_statistics(data):
    """
    Generates descriptive statistics for the numerical columns.

    Parameters:
        data (DataFrame): The country records.

    Returns:
        DataFrame: Descriptive statistics of numerical columns.
    """

    numerical_data = data[
        ["year", "lifeExp", "pop", "gdpPercap"]
    ]

    statistics = numerical_data.describe()

    return statistics