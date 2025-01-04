import csv
import os
import shutil
from typing import Any, Callable, Dict, List

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RESOURCES_PATH = os.path.join(ROOT_PATH, "resources", "repositories")
RESULTS_PATH = os.path.join(ROOT_PATH, "results")
CHARTS_PATH = os.path.join(RESULTS_PATH, "charts")
LOGS_PATH = os.path.join(ROOT_PATH, "logs")
COMMITS_PATH = os.path.join(ROOT_PATH, "commits")

def create_directory(path: str, delete_existing: bool = False):
    """
    Creates a directory at the specified path if it does not exist.
    @param path: The path of the directory to be created
    """
    if delete_existing and os.path.exists(path):
        shutil.rmtree(path)

    os.makedirs(path, exist_ok=not delete_existing)
    return path

def file_exists(path: str):
    '''
    Checks if a file exists
    @param path: The file's path.
    @return: True if it exists, False otherwise
    '''
    return os.path.isfile(path)

def read_csv(file_name: str) -> List[Dict[str, Any]]:
    """
    Reads a CSV file from the 'results/' directory and returns its content as a list of dictionaries.

    @param file_name: The name of the CSV file (without the '.csv' extension).
    @return: A list of dictionaries representing rows in the CSV file.
    """
    file_path = os.path.join(RESULTS_PATH, f"{file_name}.csv")
    if not file_exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return [row for row in reader]

def write_csv(content: List[List[Any]], file_name: str) -> None:
    """
    Writes content to a CSV file under 'results/'.
    @param content: Data to write to the CSV file, as a list of rows.
    @param file_name: The name of the CSV file.
    """
    if not isinstance(content, list) or not all(isinstance(row, list) for row in content):
        raise ValueError("Content must be a list of lists.")
    
    file_name = file_name if file_name.endswith(".csv") else f"{file_name}.csv"
    file_path: str = os.path.join(RESULTS_PATH, file_name)
    os.makedirs(RESULTS_PATH, exist_ok=True)
    with open(file_path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(content)

def create_or_update_csv(file_path: str, headers: list, data: list[str], row_identifier: str, recalculation_function: Callable[[list[str], list[str]], list[str]] = None):
    """
    Creates or updates a CSV file with the provided data.
    If the row identified by `row_identifier` exists, it will be updated; otherwise, a new row is added.

    @param file_path: Path to the CSV file.
    @param headers: List of headers for the CSV.
    @param data: List of data to insert or update in the CSV.
    @param row_identifier: The unique identifier for the row (e.g., a column value like author name).
    """
    if not file_exists(file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(headers)

    with open(file_path, 'r', newline='', encoding='utf-8') as csv_file:
        csv_data = list(csv.reader(csv_file))

    found_row = False
    for index, row in enumerate(csv_data):
        if row[0] == row_identifier:
            if (recalculation_function is not None):
                data = recalculation_function(data, row)
            csv_data[index] = data
            found_row = True
            break

    if not found_row:
        csv_data.append(data)

    with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(csv_data)