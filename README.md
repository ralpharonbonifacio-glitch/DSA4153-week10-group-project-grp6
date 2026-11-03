# DSA4153-week10-group-project-grp6

**Group 6 – DSA4153 Week 10 Group Programming Challenge**

## Project Overview

This project focuses on processing and analyzing a Gapminder historical teaching dataset using Python. It supports multiple input formats, data validation, duplicate detection, reconciliation, and data analysis.

The dataset contains historical country-level observations from 1952 to 2007. It includes deliberately introduced invalid records and duplicate entries for testing data-processing capabilities.

## Project Structure

```text
DSA4153-week10-group-project-grp6/
│
├── data/                   # Input datasets and manifest
├── output/                 # Generated outputs and reports
├── src/                    # Source code modules
├── tests/                  # Automated tests
│
├── config.json             # Project configuration
├── requirements.txt        # Python dependencies
├── main.py                 # Main program entry point
├── report.ipynb            # Analysis notebook
├── report.html             # Exported analysis report
└── README.md               # Project documentation
```

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

## Testing

Automated tests will be implemented using pytest.

```bash
python -m pytest
```

## Group Members and Responsibilities

To be updated with the final member assignments.

## Notes

- The dataset is a historical teaching snapshot, not a representation of current country statistics.
- Invalid records and duplicate entries are intentionally included for testing.
- Follow the project's configuration and validation rules when processing the dataset.
