# DSA4153-week10-group-project-grp6

**Group 6 – DSA4153 Week 10 Group Programming Challenge**

## Project Overview

This project focuses on processing and analyzing a Gapminder historical teaching dataset using Python. It supports multiple input formats, data validation, duplicate detection, data reconciliation, and data analysis.

The dataset contains historical country-level observations from 1952 to 2007. It includes deliberately introduced invalid records and duplicate entries for testing data-processing capabilities.

## Project Structure

```text
DSA4153-week10-group-project-grp6/
│
├── data/
│   └── manifest.json
│
├── output/
│
├── src/
│   ├── readers_csv_excel.py
│   ├── exports_csv_excel.py
│   ├── readers_json_parquet.py
│   ├── exports_json_parquet.py
│   ├── validation.py
│   ├── reconciliation.py
│   ├── analysis.py
│   ├── analysis_exports.py
│   ├── configuration.py
│   └── pipeline.py
│
├── tests/
│   ├── test_csv_excel.py
│   ├── test_json_parquet.py
│   ├── test_validation.py
│   ├── test_analysis.py
│   └── test_pipeline.py
│
├── FUNCTION_SPECIFICATIONS.md
├── PROJECT_GUIDELINES.md
├── README.md
├── config.json
├── main.py
├── pytest.ini
└── requirements.txt
```

**Additional files assigned for reporting:**
- `report.ipynb` – Jupyter Notebook containing the data analysis and visualizations.
- `report.html` – Exported HTML version of the analysis report.

*Note: The structure above represents the planned project organization. Some source, test, and report files may still be under development.*

## Project Documentation

The repository includes documentation and configuration files that guide the development and execution of the project.

- **`PROJECT_GUIDELINES.md`** – Contains the overall project instructions, requirements, and implementation guidelines that all group members must follow.
- **`FUNCTION_SPECIFICATIONS.md`** – Defines the required functions, expected parameters, return values, and behavior of the assigned modules.
- **`config.json`** – Contains the project configuration used by the processing pipeline.
- **`data/manifest.json`** – Defines the input dataset schema, column mappings, data types, validation rules, and expected control totals.
- **`pytest.ini`** – Contains the pytest configuration for running automated tests.
- **`requirements.txt`** – Lists the Python dependencies required by the project.

## Requirements

- Python 3.14.1
- pandas
- NumPy
- openpyxl
- PyArrow
- pytest
- Jupyter
- nbconvert

## Installation

1. Clone the repository:

```bash
git clone https://github.com/ralpharonbonifacio-glitch/DSA4153-week10-group-project-grp6.git
```

2. Navigate to the project directory:

```bash
cd DSA4153-week10-group-project-grp6
```

3. Install the required packages:

```bash
python -m pip install -r requirements.txt
```

## Input Data

The project supports the following input formats:

- CSV
- Excel (.xlsx)
- JSON
- Parquet

Refer to `data/manifest.json` for the dataset schema, column mappings, data types, validation rules, and expected control totals.

## Group Members and Responsibilities

The project is divided into five main responsibilities:

### Member 1 – CSV and Excel Processing

**Andrei Karl Dela Cruz**

Main responsibility: Handle CSV and Excel files.

Files:
- `src/readers_csv_excel.py`
- `src/exports_csv_excel.py`
- `tests/test_csv_excel.py`

Tasks:
- Read and parse CSV files.
- Read Excel files using openpyxl or pandas.
- Handle different column names and layouts specified in `manifest.json`.
- Apply the correct encoding, delimiters, and sheet names.
- Export cleaned data into CSV and Excel formats.
- Create tests for reading and exporting both formats.
- Test whether exported files can be read back correctly.

### Member 2 – JSON and Parquet Processing

**Matthew Zachary Medallon**

Main responsibility: Handle JSON and Parquet files.

Files:
- `src/readers_json_parquet.py`
- `src/exports_json_parquet.py`
- `tests/test_json_parquet.py`

Tasks:
- Read and parse JSON files.
- Flatten nested JSON structures.
- Read Parquet files using PyArrow.
- Handle different column names and data types.
- Validate values before converting them into their proper types.
- Export cleaned data into JSON and Parquet formats.
- Create tests for reading and exporting both formats.
- Test whether exported files can be read back correctly.

### Member 3 – Data Validation and Reconciliation

**Eivrard Seraphim Franco**

Main responsibility: Ensure that the data is valid, consistent, and free from duplicates.

Files:
- `src/validation.py`
- `src/reconciliation.py`
- `tests/test_validation.py`

Tasks:
- Validate all six canonical columns.
- Check missing, invalid, and unsupported values.
- Apply the validation rules in `manifest.json`.
- Identify and quarantine invalid records.
- Detect exact duplicate records.
- Detect conflicting `(country, year)` keys.
- Reconcile records from different file formats.
- Generate validation and audit reports.
- Create tests for valid records, invalid records, duplicates, and conflicting keys.

### Member 4 – Data Analysis and Reporting

**Ralph Aron Bonifacio**

Main responsibility: Analyze the cleaned dataset and present the results.

Files:
- `src/analysis.py`
- `src/analysis_exports.py`
- `tests/test_analysis.py`
- `report.ipynb`
- `report.html`

Tasks:
- Use pandas and NumPy for data analysis.
- Generate descriptive statistics.
- Analyze life expectancy, population, and GDP per capita.
- Create country-level and continent-level summaries.
- Analyze changes across the available years.
- Create appropriate visualizations.
- Export analytical results.
- Prepare the Jupyter Notebook and HTML report.
- Test the accuracy of the analytical outputs.

### Member 5 – Pipeline, Configuration, and Integration

**Josef Jayden Nepomuceno**

Main responsibility: Connect all components and make the entire program run.

Files:
- `src/configuration.py`
- `src/pipeline.py`
- `main.py`
- `tests/test_pipeline.py`

Tasks:
- Load and interpret `config.json`.
- Create the main pipeline connecting the readers, validation, reconciliation, and analysis modules.
- Implement the command-line entry point.
- Handle unsupported input formats.
- Ensure failed runs stop properly and return a nonzero exit code.
- Ensure outputs are written only when the required processing succeeds.
- Create end-to-end tests.
- Coordinate integration with the other members.

Each member is responsible for implementing and testing their assigned modules and providing a tested interface for integration. Members should coordinate with one another when their modules depend on the outputs or interfaces of other components.

## Testing

Automated tests are implemented using pytest.

To run all tests:

```bash
python -m pytest
```

To run a specific test file:

```bash
python -m pytest tests/test_analysis.py -v
```

Replace `test_analysis.py` with the test file you want to run.

## Notes

- The dataset is a historical teaching snapshot, not a representation of current country statistics.
- Invalid records and duplicate entries are intentionally included for testing.
- Follow the project's configuration and validation rules when processing the dataset.
- The processing pipeline depends on the successful integration of the input readers, validation, reconciliation, and analysis modules.
- Analytical reports should be generated using the validated and reconciled dataset.
