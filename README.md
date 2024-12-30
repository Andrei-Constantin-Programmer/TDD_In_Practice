[![Python CI](https://github.com/Andrei-Constantin-Programmer/TDD_In_Practice/actions/workflows/python-app.yml/badge.svg)](https://github.com/Andrei-Constantin-Programmer/TDD_In_Practice/actions/workflows/python-app.yml)

This is a project created as part of the Software Development Practice (COMP0104) assignment 2 at University College London (UCL).

## Table of Contents
- [Installing](#installing)
- [Run](#run)
  - [Run Tests](#run-tests)
  - [Run Analysis](#run-analysis)
- [Command-Line Interface (CLI)](#command-line-interface-cli)
- [Help](#help)
- [Project Structure](#project-structure)

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
python tdd_analysis.py [--date DATE] [--language LANGUAGE] [--languages LANGUAGES ...] [--verbose]
```
### Parameters
- --date DATE (optional): The date for the experiment in YYYY-MM-DD format. Defaults to a specific date in tdd_analysis.py.  
- --language LANGUAGE (optional): Single programming language to analyse. Defaults to Java.  
    **Note:** If this argument is provided, the '--languages' argument will be ignored  
- --languages LANGUAGES ... (optional): List of programming languages to analyze. Defaults to ['Java', 'Python', 'Kotlin', 'C#', 'Rust'].  
    **Note**: If the '--language' argument is provided, this list is ignored.  
- --verbose (optional): Enable verbose output for debugging or detailed logs.  

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