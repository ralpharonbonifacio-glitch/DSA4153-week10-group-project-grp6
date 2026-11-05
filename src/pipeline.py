import json
import os
import shutil
import sys

import numpy as np
import pandas as pd

from src.configuration import load_manifest
from src.readers_csv_excel import read_csv_file, read_excel_file
from src.readers_json_parquet import read_json_file, read_parquet_file
from src.validation import detect_conflicts, load_rules, remove_duplicates, validate_data
from src.analysis import (build_population_matrix, index_by_broadcast,
                          index_by_loop, region_population_numpy)
from src.analysis_exports import export_analysis_results
from src.exports_csv_excel import export_to_csv, export_to_excel
from src.exports_json_parquet import export_to_json, export_to_parquet

READERS = {"csv": read_csv_file, "xlsx": read_excel_file,
           "json": read_json_file, "parquet": read_parquet_file}
TOLERANCE = 1e-8
CSV_EXPORT_SETTINGS = {"sep": ";", "encoding": "cp1252"}
SIX_COLUMNS = ["country", "continent", "year", "lifeExp", "pop", "gdpPercap"]
CHECK_COLUMNS = ["check", "expected", "actual", "tolerance", "pass"]
AUDIT_COLUMNS = ["step", "source_file", "operation", "rule", "rows_before", "rows_after"]
QUARANTINE_COLUMNS = ["source_file", "source_record", "reason"] + SIX_COLUMNS
DUPLICATE_COLUMNS = ["source_file", "source_record"] + SIX_COLUMNS


class PipelineRun:
    """Holds the configuration, audit list, checks, and rejected records of one run."""

    def __init__(self, config: dict) -> None:
        self.config = config
        self.audit = []        # one dict per processing step
        self.checks = []       # one dict per validation check
        self.quarantine = []   # invalid records from all inputs
        self.duplicates = []   # removed duplicate copies from all inputs

    def log(self, step: str, source_file: str, operation: str, rule: str,
            rows_before: int, rows_after: int) -> None:
        """Add one audit record."""
        self.audit.append({"step": step, "source_file": source_file,
                           "operation": operation, "rule": rule,
                           "rows_before": rows_before, "rows_after": rows_after})

    def check(self, name: str, expected, actual, tolerance=None) -> bool:
        """Record a check; with a tolerance compare the difference, else exactly."""
        if tolerance is None:
            ok = expected == actual
        else:
            ok = abs(expected - actual) <= tolerance
        self.checks.append({"check": name, "expected": expected, "actual": actual,
                            "tolerance": "" if tolerance is None else tolerance,
                            "pass": bool(ok)})
        return bool(ok)

    def passed(self) -> bool:
        """Return True if every recorded check passed."""
        return all(c["pass"] for c in self.checks)


# recover file functions

def _record_rows(table: pd.DataFrame, source_file: str, reasons: bool) -> list[dict]:
    """Turn rejected or duplicate rows into report rows (source_record = index + 1)."""
    rows = []
    for position, row in table.iterrows():
        record = {"source_file": source_file, "source_record": int(position) + 1}
        if reasons:
            record["reason"] = row["reject_reason"]
        record.update({column: row[column] for column in SIX_COLUMNS})
        rows.append(record)
    return rows


def recover_one(spec: dict, manifest: dict, run: PipelineRun) -> pd.DataFrame:
    """Read, validate, deduplicate, and conflict-check one input file."""
    name = spec["file"]
    path = os.path.join(run.config["input_directory"], name)
    fmt = spec.get("format") or os.path.splitext(name)[1].lstrip(".")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"input file not found: {path}")
    if fmt not in run.config.get("supported_formats", list(READERS)) or fmt not in READERS:
        raise ValueError(f"unsupported input format {fmt!r} for {name}")

    # The readers take their settings from a manifest, so give each one a manifest whose only file entry is this input's settings from config.json.
    reader_manifest = dict(manifest)
    reader_manifest["files"] = [{**spec, "format": fmt, "source_to_canonical":
                                 spec.get("mapping") or spec.get("source_to_canonical", {})}]
    raw = READERS[fmt](path, reader_manifest)  # renames columns; missing column raises
    run.log("read", name, f"parse {fmt} and rename columns",
            "documented layout and mapping", len(raw), len(raw))

    result = validate_data(raw, load_rules(manifest))
    valid, rejected = result["valid"], result["rejected"]
    run.log("validate", name, "quarantine invalid records", "manifest rules",
            len(raw), len(valid))

    unique, removed = remove_duplicates(valid)
    run.log("deduplicate", name, "remove exact duplicates", "all six fields equal",
            len(valid), len(unique))

    conflicts = detect_conflicts(unique)
    if not conflicts.empty: 
        keys = conflicts[manifest["key"]].drop_duplicates().values.tolist()
        raise ValueError(f"{name}: conflicting (country, year) keys {keys[:3]}")
    run.log("conflict check", name, "same key, different values", "stop on conflict",
            len(unique), len(unique))

    clean = unique.sort_values(manifest["key"]).reset_index(drop=True)
    quarantined = _record_rows(rejected, name, reasons=True)
    duplicates = _record_rows(removed, name, reasons=False)
    run.quarantine.extend(quarantined)
    run.duplicates.extend(duplicates)
    run.check(f"{name}: raw = rejected + duplicates + canonical",
              len(raw), len(quarantined) + len(duplicates) + len(clean))
    return clean


# comparison functions

def _compare(reference: pd.DataFrame, other: pd.DataFrame, label: str,
             manifest: dict, run: PipelineRun) -> bool:
    """Compare two tables by key: exact text and integers, floats within TOLERANCE."""
    schema, order, key = manifest["canonical_schema"], manifest["canonical_order"], manifest["key"]
    if not run.check(f"{label}: columns", set(order), set(other.columns)):
        return False
    ref = reference[order].sort_values(key).reset_index(drop=True)
    oth = other[order].sort_values(key).reset_index(drop=True)

    same_keys = set(map(tuple, ref[key].to_numpy().tolist())) == \
        set(map(tuple, oth[key].to_numpy().tolist()))
    ok = run.check(f"{label}: identical keys", True, same_keys)
    ok &= run.check(f"{label}: row count", len(ref), len(oth))
    if not ok:
        return False

    text = [c for c in order if schema[c] == "string"]
    ints = [c for c in order if schema[c] == "int64"]
    floats = [c for c in order if schema[c] == "float64"]
    diff = np.abs(ref[floats].to_numpy(float) - oth[floats].to_numpy(float))
    ok &= run.check(f"{label}: text values", True,
                    bool((ref[text].to_numpy() == oth[text].to_numpy()).all()))
    ok &= run.check(f"{label}: integer values", True,
                    bool((ref[ints].to_numpy() == oth[ints].to_numpy()).all()))
    ok &= run.check(f"{label}: missingness", True,
                    bool((ref.isna().to_numpy() == oth.isna().to_numpy()).all()))
    ok &= run.check(f"{label}: float max abs difference", 0.0,
                    float(np.nan_to_num(diff, nan=0.0).max()), TOLERANCE)
    return ok


def compare_tables(tables: dict, manifest: dict, run: PipelineRun) -> pd.DataFrame:
    """Check that all recovered tables agree; return the canonical table if they do."""
    names = list(tables)
    reference = tables[names[0]]
    ok = run.check(f"{names[0]}: (country, year) keys unique", 0,
                   int(reference.duplicated(manifest["key"]).sum()))
    for name in names[1:]:
        ok &= _compare(reference, tables[name], f"agreement {names[0]} vs {name}",
                       manifest, run)
    run.log("reconcile", "all inputs", "compare tables by key", "atol 1e-8, rtol 0",
            len(names), 1)
    if not ok:
        raise ValueError("recovered tables do not agree")
    return reference[manifest["canonical_order"]].sort_values(
        manifest["key"]).reset_index(drop=True)


def check_domains(canonical: pd.DataFrame, manifest: dict, run: PipelineRun) -> None:
    """Check columns, key uniqueness, and allowed years and continents (sets)."""
    order = manifest["canonical_order"]
    run.check("canonical columns match schema", set(order), set(canonical.columns))
    run.check("canonical column order", list(order), list(canonical.columns))
    run.check("(country, year) keys unique", 0,
              int(canonical.duplicated(manifest["key"]).sum()))
    run.check("years outside allowed set", set(),
              set(canonical["year"]) - set(manifest["allowed_years"]))
    run.check("continents outside allowed set", set(),
              set(canonical["continent"]) - set(manifest["allowed_continents"]))


def check_controls(canonical: pd.DataFrame, manifest: dict, run: PipelineRun) -> None:
    """Compare counts with the manifest's expected values and control totals."""
    n_inputs = len(run.config["inputs"])
    expected = manifest["expected_per_file"]
    controls = manifest["controls"]
    run.check("canonical rows", expected["canonical_rows"], len(canonical))
    run.check("countries", controls["countries"], canonical["country"].nunique())
    run.check("Philippines rows", controls["philippines_rows"],
              int((canonical["country"] == "Philippines").sum()))
    run.check("quarantined records, all inputs",
              expected["rejected_rows"] * n_inputs, len(run.quarantine))
    run.check("duplicate copies removed, all inputs",
              expected["exact_duplicates_removed"] * n_inputs, len(run.duplicates))
    if run.config["reporting_year"] == 2007:  # the manifest controls are for 2007
        is_2007 = canonical["year"] == 2007
        asia = canonical.loc[is_2007 & (canonical["continent"] == "Asia")]
        philippines = canonical.loc[is_2007 & (canonical["country"] == "Philippines"), "pop"]
        run.check("Asia 2007 rows", controls["asia_2007_rows"], len(asia))
        run.check("Asia 2007 population", controls["asia_2007_population"],
                  int(asia["pop"].sum()))
        run.check("Philippines 2007 population",
                  controls["philippines_2007_population"], int(philippines.sum()))


# analysis functions

def asia_selected_year_table(data: pd.DataFrame, region: str, year: int) -> pd.DataFrame:
    """Rows for one continent and year, with population in millions and life-expectancy rank."""
    selected = data.loc[(data["continent"] == region) & (data["year"] == year)].copy()
    selected["pop_millions"] = selected["pop"] / 1_000_000
    selected["lifeExp_rank"] = selected["lifeExp"].rank(method="min", ascending=False).astype(int)
    return selected.sort_values(["lifeExp_rank", "country"]).reset_index(drop=True)


def country_history_table(data: pd.DataFrame, country: str) -> pd.DataFrame:
    """All observations of one country, with population in millions and life-expectancy change."""
    history = data.loc[data["country"] == country].sort_values("year").copy()
    history["pop_millions"] = history["pop"] / 1_000_000
    history["lifeExp_change"] = history["lifeExp"] - history["lifeExp"].iloc[0]
    return history.reset_index(drop=True)


def build_analysis_tables(canonical: pd.DataFrame, config: dict, run: PipelineRun) -> dict:
    """Build the three analysis tables and record the NumPy checks."""
    settings = config.get("analysis", {})
    year = config["reporting_year"]
    region = settings.get("region", "Asia")
    countries = settings.get("matrix_countries", ["Philippines", "Indonesia", "Thailand"])
    years = settings.get("matrix_years", [1982, 1987, 1992, 1997, 2002, 2007])
    baseline_year = settings.get("baseline_year", years[0])
    if baseline_year not in years:
        raise ValueError(f"baseline_year {baseline_year} is not one of matrix_years {years}")
    baseline = years.index(baseline_year)
    

    selected = asia_selected_year_table(canonical, region, year)
    history = country_history_table(canonical, settings.get("history_country", "Philippines"))

    # NumPy Boolean selection and sum, computed independently of the pandas table
    numpy_count, numpy_total = region_population_numpy(canonical, region, year)
    run.check(f"{region} {year} rows: NumPy = pandas", len(selected), numpy_count)
    run.check(f"{region} {year} population: NumPy = pandas",
              int(selected["pop"].sum()), numpy_total)

    matrix = build_population_matrix(canonical, countries, years)
    index, baseline_shape, index_shape = index_by_broadcast(matrix, baseline)
    loop_index = index_by_loop(matrix, baseline)
    run.check("population matrix shape", (len(countries), len(years)), matrix.shape)
    run.check("baseline shape before broadcasting", (len(countries), 1), baseline_shape)
    run.check("index shape after broadcasting", (len(countries), len(years)), index_shape)
    run.check("broadcast vs loop max abs difference", 0.0,
              float(np.abs(index - loop_index).max()), TOLERANCE)
    run.check("baseline year index = 100", 0.0,
              float(np.abs(index[:, baseline] - 100).max()), TOLERANCE)

    population_index = pd.DataFrame(index, columns=years)
    population_index.insert(0, "country", countries)
    return {"asia_selected_year.csv": selected, "country_history.csv": history,
            "population_index.csv": population_index}


# export functions

def export_all(canonical: pd.DataFrame, folder: str) -> None:
    """Write canonical.csv, .xlsx, .json, and .parquet into the folder."""
    export_to_csv(canonical, os.path.join(folder, "canonical.csv"))
    export_to_excel(canonical, os.path.join(folder, "canonical.xlsx"))
    export_to_json(canonical, os.path.join(folder, "canonical.json"))
    export_to_parquet(canonical, os.path.join(folder, "canonical.parquet"))


def _reload(path: str, fmt: str) -> pd.DataFrame:
    """Read one exported file back with its format's reader."""
    if fmt == "csv":
        return pd.read_csv(path, **CSV_EXPORT_SETTINGS)
    if fmt == "xlsx":
        return pd.read_excel(path, sheet_name="observations", engine="openpyxl")
    if fmt == "json":
        with open(path, encoding="utf-8") as file:
            return pd.DataFrame(json.load(file))
    return pd.read_parquet(path)


def reload_and_compare(canonical: pd.DataFrame, folder: str, manifest: dict,
                       run: PipelineRun) -> None:
    """Reload each export, reapply the declared schema, and compare with canonical.

    Files do not all keep types (CSV and JSON lose them), so every column is cast
    to the manifest's type. Columns whose type had to change are listed in the audit.
    """
    schema = manifest["canonical_schema"]
    for fmt in ("csv", "xlsx", "json", "parquet"):
        reloaded = _reload(os.path.join(folder, f"canonical.{fmt}"), fmt)
        converted = []
        for column, declared in schema.items():
            wanted = "object" if declared == "string" else declared
            if str(reloaded[column].dtype) != wanted:
                converted.append(column)
            reloaded[column] = (reloaded[column].astype(str) if declared == "string"
                                else reloaded[column].astype(declared))
        run.log("reload", f"canonical.{fmt}", "reapply declared schema",
                "converted: " + (", ".join(converted) or "none"),
                len(canonical), len(reloaded))
        _compare(canonical, reloaded, f"round trip {fmt}", manifest, run)


# run and publish functions

def write_reports(run: PipelineRun, folder: str) -> None:
    """Write the quarantine, duplicate, validation, and audit reports."""
    reports = [("quarantine.csv", run.quarantine, QUARANTINE_COLUMNS),
               ("duplicate_log.csv", run.duplicates, DUPLICATE_COLUMNS),
               ("validation.csv", run.checks, CHECK_COLUMNS),
               ("audit_log.csv", run.audit, AUDIT_COLUMNS)]
    for filename, rows, columns in reports:
        pd.DataFrame(rows, columns=columns).to_csv(os.path.join(folder, filename), index=False)


def execute(config: dict, run: PipelineRun, staging: str) -> None:
    """Run every stage, writing only into the staging folder."""
    manifest = load_manifest(config)
    if config["reporting_year"] not in set(manifest["allowed_years"]):
        raise ValueError(f"reporting_year {config['reporting_year']} is not an allowed year")
    tables = {}
    for spec in config["inputs"]:
        tables[spec["file"]] = recover_one(spec, manifest, run)

    canonical = compare_tables(tables, manifest, run)  # only returns if formats agree
    check_domains(canonical, manifest, run)
    if config.get("check_controls", True):
        check_controls(canonical, manifest, run)

    analysis = build_analysis_tables(canonical, config, run)
    for filename, table in analysis.items():
        export_analysis_results(table, os.path.join(staging, filename))
    run.log("analyse", "canonical", "pandas and NumPy tables",
            f"reporting year {config['reporting_year']}", len(canonical), len(analysis))

    export_all(canonical, staging)
    run.log("export", "canonical", "write csv, xlsx, json, parquet",
            "six canonical fields, no index", len(canonical), len(canonical))
    reload_and_compare(canonical, staging, manifest, run)

    write_reports(run, staging)
    if not run.passed():
        raise ValueError("one or more validation checks failed")


def write_failed_report(run: PipelineRun, error: Exception, out_dir: str) -> None:
    """Save the checks and the error; no analytical files are written."""
    rows = run.checks + [{"check": "run_error", "expected": "no error",
                          "actual": f"{type(error).__name__}: {error}",
                          "tolerance": "", "pass": False}]
    os.makedirs(out_dir, exist_ok=True)
    pd.DataFrame(rows, columns=CHECK_COLUMNS).to_csv(
        os.path.join(out_dir, "failed_validation_report.csv"), index=False)


def run_pipeline(config: dict) -> int:
    """Run the pipeline; return 0 on success and 1 on any failure."""

    run = PipelineRun(config)
    out_dir = os.path.normpath(config["output_directory"])
    staging = out_dir + "_staging"

    try:
        shutil.rmtree(staging, ignore_errors=True)
        os.makedirs(staging)
        execute(config, run, staging)

    except Exception as error:
        shutil.rmtree(staging, ignore_errors=True)
        write_failed_report(run, error, out_dir)
        print(f"FAILED: {type(error).__name__}: {error}",file=sys.stderr)
        return 1
    
    os.makedirs(out_dir, exist_ok=True)
    for filename in os.listdir(staging):
        os.replace(os.path.join(staging, filename),os.path.join(out_dir, filename))
    shutil.rmtree(staging, ignore_errors=True)
    stale = os.path.join(out_dir, "failed_validation_report.csv")
    
    if os.path.exists(stale):
        os.remove(stale)
    print(f"OK: outputs written to {out_dir}")
    return 0