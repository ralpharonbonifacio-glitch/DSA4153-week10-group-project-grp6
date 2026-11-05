
import numpy as np
import pandas as pd
import pytest

from src.analysis import (
    generate_descriptive_statistics,
    analyze_life_expectancy,
    analyze_population,
    analyze_gdp,
    generate_continent_summary,
    analyze_yearly_trends,
    region_population_numpy,
    build_population_matrix,
    index_by_broadcast,
    index_by_loop,
    generate_country_summary,
    generate_population_index
)

from src.analysis_exports import export_analysis_results


def create_sample_data():
    return pd.DataFrame({
        "country": ["Philippines", "Japan", "Philippines", "Japan"],
        "continent": ["Asia", "Asia", "Asia", "Asia"],
        "year": [2002, 2002, 2007, 2007],
        "lifeExp": [70.0, 82.0, 72.0, 83.0],
        "pop": [80000000, 127000000, 91000000, 128000000],
        "gdpPercap": [2000.0, 30000.0, 2500.0, 32000.0]
    })


# Sample data for the required 3 x 6 NumPy matrix
def create_population_matrix_data():
    countries = ["Philippines", "Indonesia", "Thailand"]
    years = [1982, 1987, 1992, 1997, 2002, 2007]

    populations = [
        [50000000, 56000000, 62000000, 68000000, 76000000, 91000000],
        [150000000, 165000000, 185000000, 200000000, 215000000, 225000000],
        [48000000, 52000000, 56000000, 60000000, 64000000, 67000000]
    ]

    records = []

    for i, country in enumerate(countries):
        for j, year in enumerate(years):
            records.append({
                "country": country,
                "continent": "Asia",
                "year": year,
                "lifeExp": 60.0 + j,
                "pop": populations[i][j],
                "gdpPercap": 2000.0 + (j * 100)
            })

    return pd.DataFrame(records)


# Sample data for the expected Asian population total
def create_asia_2007_data():
    populations = [100000000] * 32 + [611953827]

    return pd.DataFrame({
        "country": [f"Country{i}" for i in range(33)],
        "continent": ["Asia"] * 33,
        "year": [2007] * 33,
        "lifeExp": [60.0] * 33,
        "pop": populations,
        "gdpPercap": [2000.0] * 33
    })


def test_generate_descriptive_statistics():
    data = create_sample_data()

    result = generate_descriptive_statistics(data)

    assert result.loc["count", "year"] == 4
    assert result.loc["mean", "lifeExp"] == 76.75


def test_analyze_life_expectancy():
    data = create_sample_data()

    result = analyze_life_expectancy(data)

    assert result.loc[0, "average_life_expectancy"] == 76.0
    assert result.loc[1, "average_life_expectancy"] == 77.5


def test_analyze_population():
    data = create_sample_data()

    result = analyze_population(data)

    assert result.loc[0, "total_population"] == 207000000
    assert result.loc[1, "total_population"] == 219000000


def test_analyze_gdp():
    data = create_sample_data()

    result = analyze_gdp(data)

    assert result.loc[0, "average_gdp_per_capita"] == 16000.0
    assert result.loc[1, "average_gdp_per_capita"] == 17250.0


def test_generate_continent_summary():
    data = create_sample_data()

    result = generate_continent_summary(data)

    assert result.loc[0, "continent"] == "Asia"
    assert result.loc[0, "lifeExp"] == 76.75


def test_analyze_yearly_trends():
    data = create_sample_data()

    result = analyze_yearly_trends(data)

    assert result.loc[0, "pop"] == 207000000
    assert result.loc[1, "pop"] == 219000000


def test_export_analysis_results(tmp_path):
    data = create_sample_data()
    output_path = tmp_path / "analysis_results.csv"

    result = export_analysis_results(data, output_path)

    exported_data = pd.read_csv(output_path)

    assert result is True
    assert len(exported_data) == 4
    assert list(exported_data.columns) == list(data.columns)
    pd.testing.assert_frame_equal(exported_data, data)


def test_export_analysis_results_invalid_input(tmp_path):
    output_path = tmp_path / "invalid.csv"

    with pytest.raises(TypeError):
        export_analysis_results(
            ["invalid", "data"],
            output_path
        )


def test_region_population_numpy():
    data = create_sample_data()

    result = region_population_numpy(data, "Asia", 2007)

    assert result == (2, 219000000)


def test_build_population_matrix():
    data = create_sample_data()

    result = build_population_matrix(
        data,
        ["Philippines", "Japan"],
        [2002, 2007]
    )

    assert result.shape == (2, 2)
    assert result[0, 0] == 80000000
    assert result[0, 1] == 91000000


def test_build_population_matrix_missing_country_year():
    data = create_population_matrix_data()

    data = data.drop(
        data[
            (data["country"] == "Philippines") &
            (data["year"] == 1987)
        ].index
    )

    with pytest.raises(ValueError):
        build_population_matrix(
            data,
            ["Philippines", "Indonesia", "Thailand"],
            [1982, 1987, 1992, 1997, 2002, 2007]
        )


def test_index_by_broadcast():
    matrix = np.array([
        [100, 200, 300],
        [200, 400, 600]
    ])

    result, baseline_shape, result_shape = index_by_broadcast(matrix, 0)

    assert baseline_shape == (2, 1)
    assert result_shape == (2, 3)

    np.testing.assert_array_equal(
        result,
        [[100, 200, 300], [100, 200, 300]]
    )


def test_index_by_loop():
    matrix = np.array([
        [100, 200, 300],
        [200, 400, 600]
    ])

    result = index_by_loop(matrix, 0)

    np.testing.assert_array_equal(
        result,
        [[100, 200, 300], [100, 200, 300]]
    )


def test_generate_country_summary():
    data = create_sample_data()

    result = generate_country_summary(data)

    philippines = result[result["country"] == "Philippines"]

    assert len(philippines) == 1
    assert philippines.iloc[0]["continent"] == "Asia"
    assert philippines.iloc[0]["lifeExp"] == 71.0
    assert philippines.iloc[0]["pop"] == 85500000
    assert philippines.iloc[0]["gdpPercap"] == 2250.0


# Test the required 3 x 6 population matrix
def test_required_population_matrix():
    data = create_population_matrix_data()

    countries = ["Philippines", "Indonesia", "Thailand"]
    years = [1982, 1987, 1992, 1997, 2002, 2007]

    result = build_population_matrix(data, countries, years)

    assert result.shape == (3, 6)

    assert result[0, 0] == 50000000
    assert result[1, 0] == 150000000
    assert result[2, 0] == 48000000


# Test the 1982 baseline and broadcasting shapes
def test_required_population_broadcasting():
    data = create_population_matrix_data()

    countries = ["Philippines", "Indonesia", "Thailand"]
    years = [1982, 1987, 1992, 1997, 2002, 2007]

    matrix = build_population_matrix(data, countries, years)

    result, baseline_shape, result_shape = index_by_broadcast(matrix, 0)

    assert baseline_shape == (3, 1)
    assert result_shape == (3, 6)

    np.testing.assert_array_equal(
        result[:, 0],
        [100.0, 100.0, 100.0]
    )


# Verify broadcasting against an independent loop calculation
def test_required_broadcast_matches_loop():
    data = create_population_matrix_data()

    countries = ["Philippines", "Indonesia", "Thailand"]
    years = [1982, 1987, 1992, 1997, 2002, 2007]

    matrix = build_population_matrix(data, countries, years)

    broadcast_result, _, _ = index_by_broadcast(matrix, 0)
    loop_result = index_by_loop(matrix, 0)

    np.testing.assert_allclose(
        broadcast_result,
        loop_result
    )


# Test the expected 2007 Asian population calculation
def test_asia_population_2007_expected_total():
    data = create_asia_2007_data()

    country_count, total_population = region_population_numpy(
        data,
        "Asia",
        2007
    )

    assert country_count == 33
    assert total_population == 3811953827


# Test the complete population index generation
def test_generate_population_index():
    data = create_population_matrix_data()

    result = generate_population_index(data)

    assert result.shape == (3, 7)

    assert result["country"].tolist() == [
        "Philippines",
        "Indonesia",
        "Thailand"
    ]

    assert result[1982].tolist() == [
        100.0,
        100.0,
        100.0
    ]

    assert round(result.loc[0, 2007], 2) == 182.00
    assert round(result.loc[1, 2007], 2) == 150.00
    assert round(result.loc[2, 2007], 2) == 139.58


def test_generate_population_index_missing_country():
    data = create_population_matrix_data()

    data = data[data["country"] != "Thailand"]

    with pytest.raises(ValueError):
        generate_population_index(data)
