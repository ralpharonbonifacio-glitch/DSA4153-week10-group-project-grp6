import json
from pathlib import Path
 
import pandas as pd
import pytest
 
from src.exports_json_parquet import export_to_json, export_to_parquet
from src.readers_json_parquet import read_json_file, read_parquet_file
 
CANONICAL_ORDER = ["country", "continent", "year", "lifeExp", "pop", "gdpPercap"]
REAL_MANIFEST = Path("data/manifest.json")
REAL_JSON = Path("data/country_records.json")
REAL_PARQUET = Path("data/country_records.parquet")
 
 
@pytest.fixture
def manifest():
    """Sample manifest that uses the same structure as data/manifest.json."""
    return {
        "canonical_order": CANONICAL_ORDER,
        "files": [
            {
                "file": "test.json",
                "format": "json",
                "source_to_canonical": {
                    "identity.country": "country",
                    "identity.continent": "continent",
                    "identity.year": "year",
                    "measures.lifeExp": "lifeExp",
                    "measures.pop": "pop",
                    "measures.gdpPercap": "gdpPercap",
                },
                "encoding": "utf-8",
                "record_path": "records",
            },
            {
                "file": "test.parquet",
                "format": "parquet",
                "source_to_canonical": {
                    "COUNTRY": "country",
                    "CONTINENT": "continent",
                    "YEAR": "year",
                    "LIFE_EXP": "lifeExp",
                    "POPULATION": "pop",
                    "GDP_PER_CAPITA": "gdpPercap",
                },
                "engine": "pyarrow",
            },
        ],
    }
 
 
@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "country": ["Philippines", "Thailand"],
        "continent": ["Asia", "Asia"],
        "year": [2002, 2007],
        "lifeExp": [69.4, 70.6],
        "pop": [82995000, 65000000],
        "gdpPercap": [1516.0, 7458.0],
    })
 
 
def write_json(path, records, top_level_list=False):
    content = records if top_level_list else {
        "metadata": {"purpose": "test", "raw_records": len(records)},
        "records": records,
    }
    path.write_text(json.dumps(content), encoding="utf-8")
 
 
def nested_record(country="Philippines", year=2007):
    return {
        "identity": {"country": country, "continent": "Asia", "year": year},
        "measures": {"lifeExp": 71.688, "pop": 91077287, "gdpPercap": 3190.481016},
    }
 
 
# ---------- JSON reader ----------
 
def test_read_json_flattens_nested_records(tmp_path, manifest):
    path = tmp_path / "test.json"
    write_json(path, [nested_record(), nested_record("Thailand", 2002)])
 
    result = read_json_file(path, manifest)
 
    assert list(result.columns) == CANONICAL_ORDER
    assert len(result) == 2  # the metadata object is not a record
    assert result["country"].tolist() == ["Philippines", "Thailand"]
 
 
def test_read_json_keeps_values_unconverted(tmp_path, manifest):
    path = tmp_path / "test.json"
    write_json(path, [{
        "identity": {"country": "Philippines", "continent": "Asia", "year": "2007"},
        "measures": {"lifeExp": "71.688", "pop": "91077287", "gdpPercap": "bad"},
    }])
 
    result = read_json_file(path, manifest)
 
    assert result["year"].iloc[0] == "2007"
    assert result["gdpPercap"].iloc[0] == "bad"
 
 
def test_read_json_missing_column_is_rejected(tmp_path, manifest):
    path = tmp_path / "test.json"
    record = nested_record()
    del record["measures"]["gdpPercap"]
    write_json(path, [record])
 
    with pytest.raises(ValueError, match="Missing required columns"):
        read_json_file(path, manifest)
 
 
def test_read_json_missing_record_path(tmp_path, manifest):
    path = tmp_path / "test.json"
    path.write_text(json.dumps({"metadata": {}}), encoding="utf-8")
 
    with pytest.raises(ValueError):
        read_json_file(path, manifest)
 
 
def test_read_json_missing_file(tmp_path, manifest):
    with pytest.raises(FileNotFoundError):
        read_json_file(tmp_path / "missing.json", manifest)
 
 
def test_read_json_without_json_config(tmp_path, manifest):
    manifest["files"] = [f for f in manifest["files"] if f["format"] != "json"]
    with pytest.raises(ValueError):
        read_json_file(tmp_path / "test.json", manifest)
 
 
# ---------- Parquet reader ----------
 
def test_read_parquet_maps_columns_and_keeps_strings(tmp_path, manifest):
    pytest.importorskip("pyarrow")
    path = tmp_path / "test.parquet"
    pd.DataFrame({
        "COUNTRY": ["Philippines"], "CONTINENT": ["Asia"], "YEAR": ["2007"],
        "LIFE_EXP": ["71.688"], "POPULATION": ["91077287"],
        "GDP_PER_CAPITA": ["3190.481016"],
    }).to_parquet(path, engine="pyarrow", index=False)
 
    result = read_parquet_file(path, manifest)
 
    assert list(result.columns) == CANONICAL_ORDER
    assert result["year"].iloc[0] == "2007"
 
 
def test_read_parquet_missing_column_is_rejected(tmp_path, manifest):
    pytest.importorskip("pyarrow")
    path = tmp_path / "test.parquet"
    pd.DataFrame({"COUNTRY": ["Philippines"]}).to_parquet(path, engine="pyarrow", index=False)
 
    with pytest.raises(ValueError, match="Missing required columns"):
        read_parquet_file(path, manifest)
 
 
def test_read_parquet_missing_file(tmp_path, manifest):
    pytest.importorskip("pyarrow")
    with pytest.raises(FileNotFoundError):
        read_parquet_file(tmp_path / "missing.parquet", manifest)
 
 
# ---------- exporters ----------
 
def test_export_to_json_round_trip(tmp_path, sample_data):
    output_path = tmp_path / "output" / "result.json"
 
    result = export_to_json(sample_data, output_path)
 
    assert result == str(output_path)
    exported = pd.read_json(output_path, orient="records")
    pd.testing.assert_frame_equal(exported, sample_data, check_dtype=False)
 
 
def test_export_to_parquet_round_trip(tmp_path, sample_data):
    pytest.importorskip("pyarrow")
    output_path = tmp_path / "output" / "result.parquet"
 
    result = export_to_parquet(sample_data, output_path)
 
    assert result == str(output_path)
    exported = pd.read_parquet(output_path, engine="pyarrow")
    pd.testing.assert_frame_equal(exported, sample_data)
 
 
def test_exporters_reject_non_dataframe(tmp_path):
    with pytest.raises(TypeError):
        export_to_json(["Philippines"], tmp_path / "invalid.json")
    with pytest.raises(TypeError):
        export_to_parquet(["Philippines"], tmp_path / "invalid.parquet")
 
 
# ---------- real project files (skipped when the data folder is not present) ----------
 
def test_real_json_file_has_1712_raw_records():
    if not (REAL_MANIFEST.is_file() and REAL_JSON.is_file()):
        pytest.skip("data files not found")
    real_manifest = json.loads(REAL_MANIFEST.read_text(encoding="utf-8"))
 
    result = read_json_file(REAL_JSON, real_manifest)
 
    assert list(result.columns) == real_manifest["canonical_order"]
    assert len(result) == 1712
 
 
def test_real_parquet_file_has_1712_raw_records():
    pytest.importorskip("pyarrow")
    if not (REAL_MANIFEST.is_file() and REAL_PARQUET.is_file()):
        pytest.skip("data files not found")
    real_manifest = json.loads(REAL_MANIFEST.read_text(encoding="utf-8"))
 
    result = read_parquet_file(REAL_PARQUET, real_manifest)
 
    assert list(result.columns) == real_manifest["canonical_order"]
    assert len(result) == 1712
