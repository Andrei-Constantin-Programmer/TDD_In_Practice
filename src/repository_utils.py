import csv
from datetime import datetime
import logging
import os
import pickle
import shutil
from typing import Callable, List, Optional, Generator, Dict, Any
from pydriller import Commit
import repository_utils_core as core
from models.Repository import Repository

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESOURCES_PATH = os.path.join(ROOT_PATH, "resources", "repositories")
RESULTS_PATH = os.path.join(ROOT_PATH, "results")
LOGS_PATH = os.path.join(ROOT_PATH, "logs")
COMMITS_PATH = os.path.join(ROOT_PATH, "commits")

PLOTS_PATH = os.path.join(RESULTS_PATH, "plots")    

def create_directory(path: str, delete_existing: bool = False):
    """
    Creates a directory at the specified path if it does not exist.
    @param path: The path of the directory to be created
    """
    if delete_existing and os.path.exists(path):
        shutil.rmtree(path)

    os.makedirs(path, exist_ok=not delete_existing)
    return path

def read_repositories(language: str) -> List[Repository]:
    """
    Reads repository names from a file under 'resources/repositories/' and formats them
    as GitHub URLs from Apache (e.g., 'https://github.com/apache/{repo}.git').

    @param language: The programming language (e.g., "java", "kotlin").
    @return: A list of Repository objects.
    """
    file_path = os.path.join(RESOURCES_PATH, f"{language}_repos.txt")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    with open(file_path, "r", encoding="utf-8") as file:
        return core.read_repositories(file)


def read_csv(file_name: str) -> List[Dict[str, Any]]:
    """
    Reads a CSV file from the 'results/' directory and returns its content as a list of dictionaries.

    @param file_name: The name of the CSV file (without the '.csv' extension).
    @return: A list of dictionaries representing rows in the CSV file.
    """
    file_path = os.path.join(RESULTS_PATH, f"{file_name}.csv")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    with open(file_path, "r", encoding="utf-8") as file:
        return core.read_csv(file)


def write_csv(content: List[List[Any]], file_name: str) -> None:
    """
    Writes content to a CSV file under 'results/'.
    @param content: Data to write to the CSV file, as a list of rows.
    @param file_name: The name of the CSV file.
    """
    file_name = file_name if file_name.endswith(".csv") else f"{file_name}.csv"
    file_path: str = os.path.join(RESULTS_PATH, file_name)
    os.makedirs(RESULTS_PATH, exist_ok=True)

    with open(file_path, mode="w", encoding="utf-8", newline="") as file:
        core.write_csv(content, file)


def read_commits(repository_url: str, final_date: Optional[datetime] = None) -> Generator[Commit, None, None]:
    """
    Reads commits from a repository using PyDriller.

    @param: repository_url: The URL of the repository.
    @param: final_date: Date to read commits up until from the given repository.

    @return: A generator of Commit objects.
    """
    return core.read_commits(repository_url, final_date)


def file_exists(path: str):
    '''
    Checks if a file exists
    @param path: The file's path.
    @return: True if it exists, False otherwise
    '''
    return os.path.isfile(path)

def delete_file_if_exists(path: str):
    """
    Deletes file if it exists; if the file is deleted, log.
    @param path: The file's path
    @return: True if deleted, False if not
    """
    if os.path.isfile(path):
        os.remove(path)
        logging.notify("Deleted file: '" + path + "'")
        return True
    return False


def create_or_update_csv(file_path: str, headers: list, data: list[str], row_identifier: str, recalculation_function: Callable[[list[str]], list[str]] = None):
    """
    Creates or updates a CSV file with the provided data.
    If the row identified by `row_identifier` exists, it will be updated; otherwise, a new row is added.

    @param file_path: Path to the CSV file.
    @param headers: List of headers for the CSV.
    @param data: List of data to insert or update in the CSV.
    @param row_identifier: The unique identifier for the row (e.g., a column value like author name).
    """
    if not os.path.isfile(file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(headers)

    with open(file_path, 'r', newline='', encoding='utf-8') as csv_file:
        csv_data = list(csv.reader(csv_file))

    found_row = False
    for index, row in enumerate(csv_data):
        if row[0] == row_identifier:
            if (recalculation_function is not None):
                data = recalculation_function(data)
            csv_data[index] = data
            found_row = True
            break

    if not found_row:
        csv_data.append(data)

    with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(csv_data)

def serialize(file_path: str, data: Any):
    '''
    Serializes the given data and stores it in a file.
    @param file_path: The file where the serialized data is stored to.
    @param data: The data to serialize.
    '''
    with open(file_path, "wb") as file:
        pickle.dump(data, file)

def deserialize(file_path: str):
    '''
    Deserializes the data at the given file path.
    @param file_path: The file where the serialized data is stored to.
    @return: The deserialized data, or None if the file does not exist.
    '''
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Serialized file not found at {file_path}.")
    
    with open(file_path, "rb") as file:
        return pickle.load(file)