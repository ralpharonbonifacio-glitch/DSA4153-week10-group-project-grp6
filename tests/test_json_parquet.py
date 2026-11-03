import pytest
import os
import json
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from src.readers_json_parquet import read_json_file, read_parquet_file
from src.exports_json_parquet import export_to_json, export_to_parquet

@pytest.fixture
def mock_manifest():
    return {
        "file_mappings": {
            "json": {"country_name": "country", "cont": "continent", "yr": "year", "life_exp": "lifeExp", "population": "pop", "gdp": "gdpPercap"},
            "parquet": {"CountryStr": "country", "ContinentStr": "continent", "YearStr": "year", "LifeExpStr": "lifeExp", "PopStr": "pop", "GdpStr": "gdpPercap"}
        }
    }

@pytest.fixture
def sample_canonical_df():
    return pd.DataFrame({
        "country": ["Philippines"],
        "continent": ["Asia"],
        "year": [2007],
        "lifeExp": [71.688],
        "pop": [91077287],
        "gdpPercap": [3190.481016]
    })

def test_json_read_and_export_roundtrip(tmp_path, sample_canonical_df, mock_manifest):
    # setup test file in tmp staging
    json_path = tmp_path / "test_data.json"
    nested_data = {
        "metadata": {"source": "test", "version": 1.0},
        "records": [
            {"country_name": "Philippines", "cont": "Asia", "yr": 2007, 
             "life_exp": 71.688, "population": 91077287, "gdp": 3190.481016}
        ]
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(nested_data, f)

    # test Reader
    df_read = read_json_file(str(json_path), mock_manifest)
    assert list(df_read.columns) == ['country', 'continent', 'year', 'lifeExp', 'pop', 'gdpPercap']
    assert df_read.iloc[0]['country'] == "Philippines"

    # test Exporter
    export_path = tmp_path / "canonical.json"
    success = export_to_json(df_read, str(export_path))
    assert success is True
    assert os.path.exists(export_path)

def test_parquet_read_and_export_roundtrip(tmp_path, sample_canonical_df, mock_manifest):
    # setup Parquet file with string columns to match requirements
    parquet_path = tmp_path / "test_data.parquet"
    string_df = pd.DataFrame({
        "CountryStr": ["Philippines"], "ContinentStr": ["Asia"], "YearStr": ["2007"],
        "LifeExpStr": ["71.688"], "PopStr": ["91077287"], "GdpStr": ["3190.481016"]
    })
    table = pa.Table.from_pandas(string_df)
    pq.write_table(table, parquet_path)

    # test Reader
    df_read = read_parquet_file(str(parquet_path), mock_manifest)
    assert list(df_read.columns) == ['country', 'continent', 'year', 'lifeExp', 'pop', 'gdpPercap']
    assert df_read.iloc[0]['year'] == "2007" # validates values preserved as strings

    # test Exporter
    export_path = tmp_path / "canonical.parquet"
    success = export_to_parquet(sample_canonical_df, str(export_path))
    assert success is True
    assert os.path.exists(export_path)

def test_missing_column_rejection(tmp_path, mock_manifest):
    json_path = tmp_path / "missing_col.json"
    # omit the 'gdp' field
    nested_data = {"records": [{"country_name": "Philippines", "cont": "Asia", "yr": 2007, "life_exp": 71.688, "population": 91077287}]}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(nested_data, f)
        
    # expect file-level error
    with pytest.raises(ValueError, match="Missing required canonical columns"):
        read_json_file(str(json_path), mock_manifest)