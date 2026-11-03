# Function Specifications

This document defines the expected functions and interfaces for each project module. All members must follow these specifications to ensure compatibility during integration.

## 1. CSV and Excel Processing – Member 1

File: `src/readers_csv_excel.py`

Expected functions:
- `read_csv_file(file_path, manifest)` – Reads and parses a CSV file.
- `read_excel_file(file_path, manifest)` – Reads and parses an Excel file.

File: `src/exports_csv_excel.py`

Expected functions:
- `export_to_csv(data, output_path)` – Exports a DataFrame to CSV.
- `export_to_excel(data, output_path)` – Exports a DataFrame to Excel.

Expected return: pandas DataFrame for readers; successful export confirmation for exporters.

## 2. JSON and Parquet Processing – Member 2

File: `src/readers_json_parquet.py`

Expected functions:
- `read_json_file(file_path, manifest)` – Reads and flattens JSON records.
- `read_parquet_file(file_path, manifest)` – Reads and parses Parquet records.

File: `src/exports_json_parquet.py`

Expected functions:
- `export_to_json(data, output_path)` – Exports a DataFrame to JSON.
- `export_to_parquet(data, output_path)` – Exports a DataFrame to Parquet.

Expected return: pandas DataFrame for readers; successful export confirmation for exporters.

## 3. Validation and Reconciliation – Member 3

File: `src/validation.py`

Expected functions:
- `validate_data(data)` – Checks records against the validation rules.
- `remove_duplicates(data)` – Identifies and removes exact duplicate records.
- `detect_conflicts(data)` – Detects conflicting country-year keys.

File: `src/reconciliation.py`

Expected functions:
- `reconcile_data(dataframes)` – Combines and reconciles data from different formats.
- `generate_validation_report(results, output_path)` – Generates a validation report.

Expected return: cleaned data, rejected records, conflict information, and validation results as agreed during implementation.

## 4. Data Analysis and Reporting – Member 4

File: `src/analysis.py`

Expected functions:
- `generate_descriptive_statistics(data)` – Generates descriptive statistics.
- `analyze_life_expectancy(data)` – Analyzes life expectancy.
- `analyze_population(data)` – Analyzes population.
- `analyze_gdp(data)` – Analyzes GDP per capita.
- `generate_continent_summary(data)` – Generates continent-level summaries.
- `analyze_yearly_trends(data)` – Analyzes changes across years.

File: `src/analysis_exports.py`

Expected functions:
- `export_analysis_results(results, output_path)` – Exports analytical results.

Expected return: pandas DataFrames or structured analysis results.

## 5. Pipeline and Integration – Member 5

File: `src/configuration.py`

Expected functions:
- `load_config(config_path)` – Loads project configuration.

File: `src/pipeline.py`

Expected functions:
- `run_pipeline(config)` – Coordinates the complete processing workflow.

File: `main.py`

Responsibility:
- Provide the command-line entry point.
- Execute the pipeline.
- Handle errors and exit codes.

## General Interface Rules

- All readers must return pandas DataFrames using the canonical column names and order from `data/manifest.json`.
- All modules must use the same agreed data structure.
- Functions must have clear input parameters and return values.
- Errors must be handled consistently.
- Each member must create tests for their assigned functions.

Note: Function signatures and return structures must be reviewed by all members before implementation. Additional parameters may be agreed upon when required by the project specification.