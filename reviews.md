# Peer Code Reviews

This document records the peer code reviews conducted by the five group members. Each member is assigned to review another member's implementation. The reviewed commit, specific feedback, author response, and resulting changes are documented below.

## Review 1 – Member 1 Reviews Member 2

- **Reviewer:** Andrei Karl Dela Cruz (Member 1)
- **Member Reviewed:** Matthew Zachary Medallon (Member 2)
- **Files Reviewed:**
  - `src/readers_json_parquet.py`
  - `src/exports_json_parquet.py`
  - `tests/test_json_parquet.py`
- **Reviewed Commit:**

### Specific Feedback
[To be completed based on the actual review.]

### Author's Response
[To be completed based on the author's response.]

### Changes Made
[To be completed based on the actual changes, if any.]

---

## Review 2 – Member 2 Reviews Member 3

- **Reviewer:** Matthew Zachary Medallon (Member 2)
- **Member Reviewed:** Eivrard Seraphim Franco (Member 3)

- **Files Reviewed:**
  - `src/validation.py`
  - `src/reconciliation.py`
  - `tests/test_validation.py`
  
- **Reviewed Commits:**
  - `83a020053c3b8938b786007eb9a0653d2521c036`
  - `b91cf56034713acb91be573ba5acb55fdf9936e0`
  - `cbd50e01c0e8654ef27848af2bda5650ea9a9216`
  - `e69e4977a0565eabf703e25a1b2e7477742f52ae`
  - `1ad5d11858982ec25d6f096ca761927d1ba11cae`
  - `5e9882ec30fb89a08c5a4fb1e0c00b86fe5af861`
  - `c60161fb3d1c8ab800ca9b43564fc9aeecbe671e` 
  - `9e80bbc594bf52a5a6c50f80ad53134883461852`
  - `ffc5746efed630d47319267fa7df07141bc32108`
  - `9c38a0b41a7028df8711fee0c689a17ba0820eb1`
  - `81181f09a9bfb964052990424e3ac2eabd148ff0`
  - `a4fc2f9c55f8a265a5aff9b02e60abe871fd642c`
  - `f4aa978dab0e4cd402e6f3b53e6ec4536a4a1462`
  - `5e36c79dd3ce4f7b9e9d20309f693a8fa321f013`
  - `717c5c27022b5026b1eed4bbd1118d018bb6772c`
  - `717c5c27022b5026b1eed4bbd1118d018bb6772c`
  - `717c5c27022b5026b1eed4bbd1118d018bb6772c`

### Specific Feedback
The implementation was reviewed and found to be well-organized, highly efficient, and consistent with the assigned responsibilities. The validation.py module defines robust validation rules, effectively utilizing pandas and numpy for boundary checks, missing value detection, and type conversions based on the manifest. The reconciliation.py module handles the data integration perfectly: it successfully combines valid records, removes exact duplicates, properly quarantines conflicting keys, and generates comprehensive JSON and text audit reports.

The accompanying test suite is extremely thorough, successfully covering normal data execution, missing or non-numeric values, fractional checks, out-of-range rejections, duplicate removals, and boundary values. No major issues or required changes were identified during the review. The implementation is considered highly satisfactory and fulfills all assigned requirements without the need for revisions.

### Author's Response
No changes requested.

### Changes Made
No additional changes required following the review.

---

## Review 3 – Member 3 Reviews Member 4

- **Reviewer:** Eivrard Seraphim Franco (Member 3)
- **Member Reviewed:** Ralph Aron Mojica Bonifacio (Member 4)
- **Files Reviewed:**
  - `src/analysis.py`
  - `src/analysis_exports.py`
  - `tests/test_analysis.py`
  - `report.ipynb`
  - `report.html`
- **Reviewed Commit:**

### Specific Feedback
[To be completed based on the actual review.]

### Author's Response
[To be completed based on the author's response.]

### Changes Made
[To be completed based on the actual changes, if any.]

---

## Review 3 – Member 3 Reviews Member 4

- **Reviewer:** Eivrard Seraphim Franco (Member 3)
- **Member Reviewed:** Ralph Aron Mojica Bonifacio (Member 4)

### Files Reviewed
- `src/analysis.py`
- `src/analysis_exports.py`
- `tests/test_analysis.py`
- `report.ipynb`
- `output/report.html`

### Reviewed Commits
- `d2d70101ef4d48cfff9dfee4fe3831c7e6659bfd` – Analysis module (population index)
- `13063718481b1cb3899d78a4a9cde3099ef95495` – Analysis results export
- `3c208a349d510bb9042f458a904318dd664f9406` – Analysis tests
- `db5c6a07f6352ae3044d8775856148d6688ca53b` – Analysis notebook and HTML report

### Specific Feedback

The analysis module is well organized and follows the function specification. All six required functions are present, with clear names, docstrings and type hints. The NumPy functions (`region_population_numpy`, `build_population_matrix`, `index_by_broadcast`, `index_by_loop`) are correct. Running `tests/test_analysis.py` gave 17 passed.

The report's results are consistent with `manifest.json`: 1,704 records, 142 countries, 33 Asian countries in 2007 with a population of 3,811,953,827, and a Philippines 2007 population of 91,077,287. The broadcasting and loop calculations match, and the written interpretations agree with the tables shown. `report.html` was opened and checked. It contains the full notebook content, all 6 charts and the conclusion, with no execution errors, and it is self-contained because the images are embedded.

**Issues found (none blocking, one should be addressed):**

1. **`descriptive_statistics.csv` loses its row labels.** `export_analysis_results` always writes with `index=False`. For `describe()` output, the labels (count, mean, std, min, 25%, 50%, 75%, max) are the index, so the exported file contains only numbers and cannot be read.
2. **"Average" is unweighted but described as "global".** Average life expectancy and average GDP per capita are simple means across countries, so a small country counts as much as China. The report calls them "global averages".
3. **Error handling is not tested.** `export_analysis_results` raises an unclear `AttributeError` for a non-DataFrame, and no test covers the error paths, such as the `ValueError` in `build_population_matrix` when a country-year record is missing. No test checks the exported file's contents beyond the row count, which is how issue 1 went unnoticed.

**Minor observations:** the notebook has unused imports and needs `output/canonical.csv` from the pipeline, which is not stated, and `lifeExp_rank` appears as a decimal.

### Author's Response
[To be completed after the author responds.]

### Changes Made
[To be completed after the author makes changes, if any.]

---

## Review 5 – Member 5 Reviews Member 1

- **Reviewer:** Matthew Zachary Medallon (Member 2)
- **Member Reviewed:** Josef Jayden Nepomuceno (Member 5)
- **Files Reviewed:**
  - `src/readers_csv_excel.py`
  - `src/exports_csv_excel.py`
  - `tests/test_csv_excel.py`
- **Reviewed Commit:**

### Specific Feedback
[To be completed based on the actual review.]

### Author's Response
[To be completed based on the author's response.]

### Changes Made
[To be completed based on the actual changes, if any.]
