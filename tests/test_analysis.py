import pandas as pd

from src.analysis import (
    generate_descriptive_statistics,
    analyze_life_expectancy,
    analyze_population,
    analyze_gdp,
    generate_continent_summary,
    analyze_yearly_trends
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