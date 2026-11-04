
"""
Data Analysis Module

This module contains functions for analyzing
country-level data using pandas and NumPy.
"""

import pandas as pd
import numpy as np


def generate_descriptive_statistics(data: pd.DataFrame) -> pd.DataFrame:
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


def analyze_life_expectancy(data: pd.DataFrame) -> pd.DataFrame:
    """
    Analyzes life expectancy across countries and years.

    Returns:
        DataFrame: Average life expectancy grouped by year.
    """

    life_expectancy = data.groupby("year")["lifeExp"].mean()

    return life_expectancy.reset_index(name="average_life_expectancy")


def analyze_population(data: pd.DataFrame) -> pd.DataFrame:
    """
    Analyzes total population across years.

    Returns:
        DataFrame: Total population grouped by year.
    """

    population = data.groupby("year")["pop"].sum()

    return population.reset_index(name="total_population")


def analyze_gdp(data: pd.DataFrame) -> pd.DataFrame:
    """
    Analyzes average GDP per capita across years.

    Returns:
        DataFrame: Average GDP per capita grouped by year.
    """

    gdp = data.groupby("year")["gdpPercap"].mean()

    return gdp.reset_index(name="average_gdp_per_capita")


def generate_continent_summary(data: pd.DataFrame) -> pd.DataFrame:
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


def analyze_yearly_trends(data: pd.DataFrame) -> pd.DataFrame:
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


def region_population_numpy(
    data: pd.DataFrame,
    region: str,
    year: int
) -> tuple[int, int]:
    """
    Calculates the number of countries and total population
    in a selected continent and year using NumPy.
    """

    continents = data["continent"].to_numpy()
    years = data["year"].to_numpy()
    populations = data["pop"].to_numpy()

    selected = (continents == region) & (years == year)

    country_count = selected.sum()
    total_population = populations[selected].sum()

    return int(country_count), int(total_population)


def build_population_matrix(
    data: pd.DataFrame,
    countries: list[str],
    years: list[int]
) -> np.ndarray:
    """
    Builds a population matrix where rows represent countries
    and columns represent years.
    """

    matrix = np.zeros((len(countries), len(years)), dtype=np.int64)

    country_names = data["country"].to_numpy()
    observation_years = data["year"].to_numpy()
    populations = data["pop"].to_numpy()

    for i, country in enumerate(countries):
        for j, year in enumerate(years):

            selected = (country_names == country) & (observation_years == year)

            if selected.sum() != 1:
                raise ValueError("Expected exactly one record per country and year.")

            matrix[i, j] = populations[selected].sum()

    return matrix


def index_by_broadcast(
    matrix: np.ndarray,
    baseline_column: int
) -> tuple[np.ndarray, tuple[int, int], tuple[int, int]]:
    """
    Calculates population indexes using NumPy broadcasting.
    """

    baseline = matrix[:, [baseline_column]]
    index = matrix / baseline * 100

    return index, baseline.shape, index.shape


def index_by_loop(
    matrix: np.ndarray,
    baseline_column: int
) -> np.ndarray:
    """
    Calculates population indexes using nested loops.
    """

    result = np.zeros(matrix.shape, dtype=float)

    for i in range(matrix.shape[0]):
        baseline = float(matrix[i][baseline_column])

        for j in range(matrix.shape[1]):
            result[i][j] = matrix[i][j] / baseline * 100

    return result


def generate_country_summary(data: pd.DataFrame) -> pd.DataFrame:
    """
    Generates summary statistics grouped by country.

    Returns:
        DataFrame: Average life expectancy, population,
        and GDP per capita for each country.
    """

    country_summary = data.groupby(
        ["country", "continent"]
    ).agg({
        "lifeExp": "mean",
        "pop": "mean",
        "gdpPercap": "mean"
    })

    return country_summary.reset_index()


def generate_population_index(data: pd.DataFrame) -> pd.DataFrame:
    """
    Generates the population index for the Philippines,
    Indonesia, and Thailand from 1982 to 2007.
    """

    countries = ["Philippines", "Indonesia", "Thailand"]
    years = [1982, 1987, 1992, 1997, 2002, 2007]

    population_matrix = build_population_matrix(
        data,
        countries,
        years
    )

    if population_matrix.shape != (3, 6):
        raise ValueError("Population matrix must have a 3 x 6 shape.")

    population_index, baseline_shape, index_shape = index_by_broadcast(
        population_matrix,
        0
    )

    if baseline_shape != (3, 1) or index_shape != (3, 6):
        raise ValueError("Unexpected broadcasting shapes.")

    loop_index = index_by_loop(population_matrix, 0)

    if not np.allclose(population_index, loop_index):
        raise ValueError("Broadcasting and loop calculations do not match.")

    if not np.allclose(population_index[:, 0], 100):
        raise ValueError("The 1982 population index must equal 100.")

    result = pd.DataFrame(
        population_index,
        columns=years
    )

    result.insert(0, "country", countries)

    return result
