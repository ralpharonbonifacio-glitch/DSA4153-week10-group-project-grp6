# DSA4153 Week 10 Group Programming Challenge

## Project Overview

This project implements a data processing and analysis pipeline for the Gapminder historical dataset. It supports multiple input formats, validates and reconciles records, removes invalid and duplicate entries, and generates standardized datasets and analytical reports.

The system is designed to handle CSV, Excel, JSON, and Parquet files while applying consistent validation rules and producing reliable outputs for further analysis.

## Project Structure

```text
DSA4153-week10-group-project-grp6/
│
├── data/
│   ├── README.txt
│   ├── conflicting_key.csv
│   ├── country_records.csv
│   ├── country_records.json
│   ├── country_records.parquet
│   ├── country_records.xlsx
│   ├── manifest.json
│   ├── missing_column.csv
│   └── unsupported.txt
│
├── output/
│   ├── .gitkeep
│   ├── asia_selected_year.csv
│   ├── audit_log.csv
│   ├── canonical.csv
│   ├── canonical.json
│   ├── canonical.parquet
│   ├── canonical.xlsx
│   ├── cleaned_data.csv
│   ├── continent_summary.csv
│   ├── country_history.csv
│   ├── country_summary.csv
│   ├── descriptive_statistics.csv
│   ├── duplicate_log.csv
│   ├── gdp_analysis.csv
│   ├── life_expectancy_analysis.csv
│   ├── population_analysis.csv
│   ├── population_index.csv
│   ├── quarantine.csv
│   ├── report.html
│   ├── report.ipynb
│   ├── validation.csv
│   └── yearly_trends.csv
│
├── src/
│   ├── __init__.py
│   ├── analysis.py
│   ├── analysis_exports.py
│   ├── configuration.py
│   ├── exports_csv_excel.py
│   ├── exports_json_parquet.py
│   ├── pipeline.py
│   ├── readers_csv_excel.py
│   ├── readers_json_parquet.py
│   ├── reconciliation.py
│   └── validation.py
│
├── tests/
│   ├── __init__.py
│   ├── test_analysis.py
│   ├── test_csv_excel.py
│   ├── test_json_parquet.py
│   ├── test_pipeline.py
│   ├── test_results.txt
│   └── test_validation.py
│
├── .gitignore
├── README.md
├── config.json
├── contributions.csv
├── contributions.md
├── main.py
├── pytest.ini
├── requirements.txt
└── reviews.md
```

The final submission ZIP also includes `submission_manifest.txt` in the project root. This file records the repository URL, release tag, full commit hash, and SHA-256 hashes of the supplied input files.

## Dataset Information

The project uses a historical snapshot of the Gapminder dataset containing country-level observations from 1952 to 2007.

**Original Dataset Source:** [Gapminder Dataset](https://raw.githubusercontent.com/jennybc/gapminder/main/inst/extdata/gapminder.tsv)

**Dataset Documentation:** [Gapminder Reference](https://jennybc.github.io/gapminder/reference/gapminder.html)

### Dataset Scope

- Countries: 142
- Observation period: 1952–2007
- Observation interval: Five years
- Original observations: 1,704
- Canonical records after processing: 1,704

The supplied input files contain deliberately introduced invalid records and duplicate records for testing the pipeline. These additions are for instructional purposes and are not part of the original Gapminder dataset.

### Canonical Dataset Schema

| Column | Data Type | Description |
|---|---|---|
| country | string | Country name |
| continent | string | Continent where the country belongs |
| year | int64 | Observation year |
| lifeExp | float64 | Life expectancy in years |
| pop | int64 | Population in persons |
| gdpPercap | float64 | GDP per capita in inflation-adjusted US dollars |

The canonical record key is composed of `country` and `year`.

### Input File Formats

The pipeline supports four input formats:

- **CSV:** Handles configured encodings, delimiters, comments, column aliases, and additional columns.
- **Excel:** Reads observations from the configured worksheet and maps source columns to the canonical schema.
- **JSON:** Reads records from the configured record path and handles nested fields.
- **Parquet:** Reads Parquet files and validates source values before converting them to their required data types.

The input configuration and format-specific settings are defined in `data/manifest.json`.

### Expected Input Record Counts

Each of the four main input files contains:

| Record Category | Expected Count |
|---|---:|
| Raw records | 1,712 |
| Invalid records rejected | 6 |
| Valid records before deduplication | 1,706 |
| Exact duplicates removed | 2 |
| Canonical records | 1,704 |

The pipeline also includes separate failure-test files:

- `conflicting_key.csv` contains a contradictory record for an existing country-year key and must cause processing to fail.
- `missing_column.csv` is missing the required `pop` column and must cause processing to fail.
- `unsupported.txt` is an unsupported input format and must be rejected.

## Main Features

### 1. Multiple File Format Support

Reads and processes CSV, Excel, JSON, and Parquet datasets using their respective readers.

### 2. Data Validation

Checks records against the configured schema and validation rules, including required columns, valid country and continent values, allowed years, numeric values, and permitted value ranges.

### 3. Data Reconciliation

Identifies and rejects invalid records, removes exact duplicate records, and detects conflicting country-year keys.

### 4. Standardized Data Export

Exports processed records into standardized CSV, Excel, JSON, and Parquet formats.

### 5. Data Analysis

Generates descriptive statistics and country-level analytical summaries using the processed dataset.

### 6. Reporting and Visualization

Produces analytical reports and visualizations using Matplotlib. The project includes an HTML report and Jupyter Notebook for presenting the results.

### 7. Automated Testing

Uses pytest to test the readers, validation rules, reconciliation process, analysis functions, and overall pipeline.

## Installation and Setup

### Requirements

- Python 3.14.1
- pandas 3.0.5
- NumPy 2.5.3
- openpyxl 3.1.5
- PyArrow 26.0.0
- pytest 9.2.0
- Jupyter 1.1.1
- nbconvert 7.17.1
- Matplotlib 3.11.2

All required Python packages and their exact versions are specified in `requirements.txt`.

### 1. Clone the Repository

```bash
git clone https://github.com/ralpharonbonifacio-glitch/DSA4153-week10-group-project-grp6.git
```

### 2. Navigate to the Project Directory

```bash
cd DSA4153-week10-group-project-grp6
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment:

**Windows:**

```bash
venv\Scripts\activate
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Project

Run the main program from the project root directory:

```bash
python main.py
```

The program uses the configuration and input files provided in the project to execute the data processing pipeline.

## Running the Tests

To execute the complete test suite, run:

```bash
pytest -v
```

The test files are located in the `tests/` directory and cover the individual components and overall pipeline.

## Reports and Outputs

The `output/` directory contains the generated pipeline outputs and analytical reports.

These include:

- **Standardized datasets:** `canonical.csv`, `canonical.json`, `canonical.parquet`, and `canonical.xlsx`.
- **Cleaned data:** `cleaned_data.csv`.
- **Data quality records:** `quarantine.csv`, `duplicate_log.csv`, and `validation.csv`.
- **Audit information:** `audit_log.csv`.
- **Analytical outputs:** `asia_selected_year.csv`, `continent_summary.csv`, `country_history.csv`, `country_summary.csv`, `descriptive_statistics.csv`, `gdp_analysis.csv`, `life_expectancy_analysis.csv`, `population_analysis.csv`, `population_index.csv`, and `yearly_trends.csv`.
- **Jupyter Notebook:** `report.ipynb`, containing the analysis and report.
- **HTML Report:** `report.html`, the HTML export of the analytical report.

All required generated outputs, including the notebook and HTML report, are included in the final submission package.

## Group Members and Responsibilities

| Group Member | Main Responsibility |
|---|---|
| Andrei Karl Dela Cruz | CSV and Excel readers and related processing |
| Matthew Zachary Medallon | JSON and Parquet readers and related processing |
| Eivrard Seraphim Franco | Data validation and reconciliation |
| Ralph Aron Bonifacio | Data analysis and reporting |
| Josef Jayden Nepomuceno | Pipeline development and integration |

## Contribution and Review Records

The project includes the following files for documenting individual contributions and code reviews:

- `contributions.csv` – Records individual contributions and supporting implementation details.
- `contributions.md` – Provides a summary of group member contributions.
- `reviews.md` – Documents code review activities and feedback.

## Release and Submission Information

**GitHub Repository:**  
https://github.com/ralpharonbonifacio-glitch/DSA4153-week10-group-project-grp6

**Release Tag:** `week10-v1.0`

The final submission ZIP includes the project source code, configuration files, supplied input data, generated outputs, automated tests, reports, contribution and review records, and `submission_manifest.txt`.

The submission manifest contains the release commit hash and SHA-256 hashes of the supplied input files to support verification of the submitted materials.

## Notes

- The `data/manifest.json` file contains the dataset configuration, schema definitions, input format settings, validation rules, and expected control values.
- The supplied dataset includes intentionally introduced defects for testing data validation and reconciliation.
- The original Gapminder observations cover 1952–2007 and should not be interpreted as current country statistics.
- Generated outputs required by the assignment must be present in the final submission package.