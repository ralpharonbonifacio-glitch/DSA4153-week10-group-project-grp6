# Project Guidelines

## 1. Python Coding Conventions

All members must follow these conventions:

- Use `snake_case` for variables and function names.
- Use `UPPER_CASE` for constants.
- Use 4 spaces for indentation.
- Use clear and descriptive names.
- Avoid unnecessary complicated code.
- Add comments when the logic needs explanation.

## 2. Canonical Data Structure

All file readers must return a pandas DataFrame using the following canonical columns in this exact order:

1. `country`
2. `continent`
3. `year`
4. `lifeExp`
5. `pop`
6. `gdpPercap`

All members must follow the same column names and data types defined in `data/manifest.json`.

## 3. Git Branching Convention

Each member must work on their assigned branch.

Suggested branch names:

- `member1-csv-excel`
- `member2-json-parquet`
- `member3-validation`
- `member4-analysis`
- `member5-integration`

Do not directly commit individual task changes to `main`.

## 4. Commit Message Convention

Use the following format:

`type: description`

Examples:

- `feat: add csv reader`
- `fix: handle invalid records`
- `test: add validation tests`
- `docs: update project documentation`
- `chore: update project configuration`

## 5. Pull Request Guidelines

1. Push completed changes to your assigned branch.
2. Create a Pull Request targeting `main`.
3. Provide a short description of your changes.
4. Include relevant tests.
5. Request another member to review your changes.
6. Merge only after the changes have been reviewed and approved.

## 6. Testing Guidelines

Use pytest for automated testing.

Run all tests using:

`python -m pytest`

Each member is responsible for testing their assigned module.

## 7. File Management

- Place source code inside `src/`.
- Place automated tests inside `tests/`.
- Keep original input datasets inside `data/`.
- Save generated outputs inside `output/`.
- Do not modify the original input datasets.
- Do not commit temporary files or unnecessary generated files.

## 8. Dependencies

Install project dependencies using:

`python -m pip install -r requirements.txt`

All members should use the same Python version and package versions specified by the project.