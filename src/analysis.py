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

def analyze_life_expectancy(data):
    """
    Analyzes life expectancy across countries and years.

    Returns:
        DataFrame: Average life expectancy grouped by year.
    """

    life_expectancy = data.groupby("year")["lifeExp"].mean()

    return life_expectancy.reset_index(name="average_life_expectancy")

def analyze_population(data):
    """
    Analyzes total population across years.

    Returns:
        DataFrame: Total population grouped by year.
    """

    population = data.groupby("year")["pop"].sum()

    return population.reset_index(name="total_population")

def analyze_gdp(data):
    """
    Analyzes average GDP per capita across years.

    Returns:
        DataFrame: Average GDP per capita grouped by year.
    """

    gdp = data.groupby("year")["gdpPercap"].mean()

    return gdp.reset_index(name="average_gdp_per_capita")

def generate_continent_summary(data):
    """
    Generates summary statistics grouped by continent.

    Returns:
        DataFrame: Average life expectancy, population,
        and GDP per capita for each continent.
    """

    continent_summary = data.groupby("continent").agg({
        "lifeExp": "mean",
        "pop": "mean",
        "gdpPercap": "mean"
    })

    return continent_summary.reset_index()

def analyze_yearly_trends(data):
    """
    Analyzes yearly changes in life expectancy,
    population, and GDP per capita.

    Returns:
        DataFrame: Average values grouped by year.
    """

    yearly_trends = data.groupby("year").agg({
        "lifeExp": "mean",
        "pop": "sum",
        "gdpPercap": "mean"
    })

    return yearly_trends.reset_index()
