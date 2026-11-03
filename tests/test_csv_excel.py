"""Tests for CSV and Excel readers and exporters."""

import pandas as pd
import pytest

from src.readers_csv_excel import read_csv_file, read_excel_file
from src.exports_csv_excel import export_to_csv, export_to_excel


@pytest.fixture
def manifest():
    """Provide a sample manifest for testing."""
    return {
        "canonical_order": [
            "country", "continent", "year",
            "lifeExp", "pop", "gdpPercap"
        ],
        "canonical_schema": {
            "country": "string",
            "continent": "string",
            "year": "int64",
            "lifeExp": "float64",
            "pop": "int64",
            "gdpPercap": "float64",
        },
        "files": [
            {
                "file": "test.csv",
                "format": "csv",
                "source_to_canonical": {
                    "CountryName": "country",
                    "ContinentName": "continent",
                    "ObservationYear": "year",
                    "LifeYears": "lifeExp",
                    "PopulationPersons": "pop",
                    "GDPPerPerson": "gdpPercap",
                },
                "encoding": "cp1252",
                "separator": ";",
                "comment_prefix": "#",
                "ignore_columns": ["export_note"],
            },
            {
                "file": "test.xlsx",
                "format": "xlsx",
                "source_to_canonical": {
                    "country_name": "country",
                    "continent_name": "continent",
                    "observation_year": "year",
                    "life_expectancy": "lifeExp",
                    "population": "pop",
                    "gdp_per_capita": "gdpPercap",
                },
                "sheet_name": "observations",
                "engine": "openpyxl",
            },
        ],
    }


@pytest.fixture
def sample_data():
    """Create sample canonical data for testing."""
    return pd.DataFrame({
        "country": ["Philippines", "Thailand"],
        "continent": ["Asia", "Asia"],
        "year": [2002, 2007],
        "lifeExp": [69.4, 70.6],
        "pop": [82995000, 65000000],
        "gdpPercap": [1516.0, 7458.0],
    })


def test_read_csv_file(tmp_path, manifest, sample_data):
    csv_path = tmp_path / "test.csv"

    original_data = pd.DataFrame({
        "CountryName": sample_data["country"],
        "ContinentName": sample_data["continent"],
        "ObservationYear": sample_data["year"],
        "LifeYears": sample_data["lifeExp"],
        "PopulationPersons": sample_data["pop"],
        "GDPPerPerson": sample_data["gdpPercap"],
        "export_note": ["sample", "sample"],
    })

    original_data.to_csv(
        csv_path,
        sep=";",
        index=False,
        encoding="cp1252"
    )

    result = read_csv_file(csv_path, manifest)

    assert list(result.columns) == manifest["canonical_order"]
    assert "export_note" not in result.columns
    assert result["country"].tolist() == ["Philippines", "Thailand"]
    assert result["year"].tolist() == [2002, 2007]


def test_read_excel_file(tmp_path, manifest, sample_data):
    excel_path = tmp_path / "test.xlsx"

    original_data = pd.DataFrame({
        "country_name": sample_data["country"],
        "continent_name": sample_data["continent"],
        "observation_year": sample_data["year"],
        "life_expectancy": sample_data["lifeExp"],
        "population": sample_data["pop"],
        "gdp_per_capita": sample_data["gdpPercap"],
    })

    original_data.to_excel(
        excel_path,
        sheet_name="observations",
        index=False,
        engine="openpyxl"
    )

    result = read_excel_file(excel_path, manifest)

    assert list(result.columns) == manifest["canonical_order"]
    assert len(result) == 2
    assert result["country"].tolist() == ["Philippines", "Thailand"]


def test_export_to_csv(tmp_path, sample_data):
    output_path = tmp_path / "output" / "result.csv"

    result = export_to_csv(sample_data, output_path)

    assert output_path.exists()
    assert result == str(output_path)

    exported_data = pd.read_csv(
        output_path,
        sep=";",
        encoding="cp1252"
    )

    assert exported_data.shape == sample_data.shape
    assert exported_data["country"].tolist() == sample_data["country"].tolist()


def test_export_to_excel(tmp_path, sample_data):
    output_path = tmp_path / "output" / "result.xlsx"

    result = export_to_excel(sample_data, output_path)

    assert output_path.exists()
    assert result == str(output_path)

    exported_data = pd.read_excel(
        output_path,
        engine="openpyxl"
    )

    assert exported_data.shape == sample_data.shape
    assert exported_data["country"].tolist() == sample_data["country"].tolist()


def test_csv_round_trip(tmp_path, manifest, sample_data):
    output_path = tmp_path / "round_trip.csv"

    export_to_csv(sample_data, output_path)
    result = read_csv_file(output_path, manifest)

    pd.testing.assert_frame_equal(
        result.reset_index(drop=True),
        sample_data.reset_index(drop=True),
        check_dtype=False,
    )


def test_excel_round_trip(tmp_path, manifest, sample_data):
    output_path = tmp_path / "round_trip.xlsx"

    export_to_excel(sample_data, output_path)
    result = read_excel_file(output_path, manifest)

    pd.testing.assert_frame_equal(
        result.reset_index(drop=True),
        sample_data.reset_index(drop=True),
        check_dtype=False,
    )


def test_missing_csv_file(tmp_path, manifest):
    with pytest.raises(FileNotFoundError):
        read_csv_file(tmp_path / "missing.csv", manifest)


def test_missing_excel_file(tmp_path, manifest):
    with pytest.raises(FileNotFoundError):
        read_excel_file(tmp_path / "missing.xlsx", manifest)


def test_missing_required_columns(tmp_path, manifest):
    csv_path = tmp_path / "incomplete.csv"

    pd.DataFrame({
        "CountryName": ["Philippines"],
        "ContinentName": ["Asia"],
    }).to_csv(
        csv_path,
        sep=";",
        index=False,
        encoding="cp1252"
    )

    with pytest.raises(ValueError, match="Missing required columns"):
        read_csv_file(csv_path, manifest)


def test_export_rejects_non_dataframe(tmp_path):
    with pytest.raises(TypeError):
        export_to_csv(["Philippines"], tmp_path / "invalid.csv")

    with pytest.raises(TypeError):
        export_to_excel(["Philippines"], tmp_path / "invalid.xlsx")