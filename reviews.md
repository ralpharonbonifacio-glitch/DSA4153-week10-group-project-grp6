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

## Review 4 – Member 4 Reviews Member 5

- **Reviewer:** Ralph Aron Mojica Bonifacio (Member 4)
- **Member Reviewed:** Josef Jayden Nepomuceno (Member 5)

### Files Reviewed
- `src/configuration.py`
- `src/pipeline.py`
- `main.py`
- `tests/test_pipeline.py`

### Reviewed Commits
- `a5bc2a03db364c7212e8551fc011131fb05e833d` – Configuration
- `e4c13776eee75099f69859dc2f49049ca7fd5fca` – Pipeline
- `c0849ebf93d425f0da14d2e907d0ce5c56834d32` – Main entry point
- `dff81700afc1d0d35b55f098546ba942bc40e755` – Pipeline tests

### Specific Feedback

The implementation was reviewed and found to be well-organized and consistent with the assigned responsibilities. The configuration module validates the required settings, the main entry point handles command-line arguments and errors, and the pipeline integrates the different processing modules.

The test suite also covers normal pipeline execution, invalid inputs, data validation, reconciliation, export verification, failure handling, and configuration settings.

**No major issues or required changes were identified during the review.** The implementation is considered satisfactory for the assigned requirements.

### Author's Response
No changes requested.

### Changes Made
No additional changes required following the review.

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
