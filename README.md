[![Python CI](https://github.com/Andrei-Constantin-Programmer/TDD_In_Practice/actions/workflows/python-app.yml/badge.svg)](https://github.com/Andrei-Constantin-Programmer/TDD_In_Practice/actions/workflows/python-app.yml)

This is a project created as part of the Software Development Practice (COMP0104) assignment 2 at University College London (UCL).
Its role is to mine repositories (from the Apache Software Project) to see how much TDD is used in practice.

## Table of Contents
- [Installing](#installing)
- [Run Analysis](#run-analysis)
  - [Parameters](#parameters)
  - [Help](#help)
- [Run Tests](#run-tests)

## Installing

1. Ensure **Python 3.9.x** or higher is installed

2. Clone project
Clone the repository locally, or download and extract the ZIP file.

3. Install prerequisite packages
Run the following command from the project root:
    ```bash
    pip install -r requirements.txt
    ```

## Run Analysis
To execute the TDD analysis, use the command-line interface:
```bash
python tdd_analysis.py [--date DATE] [--language LANGUAGE] [--languages LANGUAGES ...]
                       [--repository REPOSITORY] [--verbose]
```

### Parameters
- `--date DATE (optional)`: The date for the experiment in YYYY-MM-DD format. Defaults to a specific date in `tdd_analysis.py`.
  
- `--language LANGUAGE (optional)`: Single programming language to analyse. Defaults to `Java`.
  
    **Note:** If this argument is provided, the `'--languages'` argument will be ignored
  
- `--languages LANGUAGES ... (optional)`: List of programming languages to analyse. Defaults to `['Java', 'Python', 'Kotlin', 'C#', 'Rust']`.
  
    **Note**: If the `'--language'` argument is provided, this list is ignored.
  
- `--repository --repo REPOSITORY (optional)`: URL for repository to analyse. By default, analyse all repos under `resources/repositories`.
  
    **Note**: The `'--language'` argument must also be provided if `'--repository'` is provided.
  
- `--verbose (optional)`: Enable verbose output for debugging or detailed logs.  

### Help
To display a help message with detailed usage instructions, run:

```bash
python tdd_analysis.py --help
```

## Run Tests
To run the unit tests, simply call:
```bash
pytest
```
