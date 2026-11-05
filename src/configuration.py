import json
from pathlib import Path
 
REQUIRED_INPUT_KEYS = {"file", "mapping"}
DEFAULT_FORMATS = ["csv", "xlsx", "json", "parquet"]
 
 
def _check_input(spec: object, position: int) -> None:
    """Raise ValueError if one input block is malformed."""
    if not isinstance(spec, dict):
        raise ValueError(f"input {position} must be an object")
    missing = REQUIRED_INPUT_KEYS - set(spec)
    if missing:
        raise ValueError(f"input {position} is missing {sorted(missing)}")
    if not isinstance(spec["file"], str) or not spec["file"].strip():
        raise ValueError(f"input {position}: 'file' must be a non-empty text value")
    mapping = spec["mapping"]
    if not (isinstance(mapping, dict) and mapping and all(
            isinstance(key, str) and isinstance(value, str) for key, value in mapping.items())):
        raise ValueError(f"input {position}: 'mapping' must map source names to canonical names")
    if "format" in spec and not isinstance(spec["format"], str):
        raise ValueError(f"input {position}: 'format' must be text")
 
 
def load_config(path: str) -> dict:
    """Read config.json, fill in defaults, and check years, formats, and inputs."""
    with open(path, encoding="utf-8") as file:
        config = json.load(file)
    if not isinstance(config, dict):
        raise ValueError("config.json must contain a JSON object")
    config.setdefault("reporting_year", 2007)
    config.setdefault("input_directory", "data")
    config.setdefault("output_directory", "output")
    config.setdefault("supported_formats", list(DEFAULT_FORMATS))
 
    year = config["reporting_year"]
    if isinstance(year, bool) or not isinstance(year, int):
        raise ValueError(f"reporting_year must be a whole number, got {year!r}")
    formats = config["supported_formats"]
    if not (isinstance(formats, list) and formats and all(isinstance(f, str) for f in formats)):
        raise ValueError("supported_formats must be a non-empty list of format names")
    inputs = config.get("inputs")
    if not isinstance(inputs, list) or not inputs:
        raise ValueError("config.json needs a non-empty 'inputs' list")
    for position, spec in enumerate(inputs, start=1):
        _check_input(spec, position)
    return config
 
 
def load_manifest(config: dict) -> dict:
    """Read manifest.json from the input directory (schema, rules, controls)."""
    manifest_path = Path(config["input_directory"]) / "manifest.json"
    with open(manifest_path, encoding="utf-8") as file:
        return json.load(file)
 