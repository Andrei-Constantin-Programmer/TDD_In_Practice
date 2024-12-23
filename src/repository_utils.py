from datetime import datetime
import logging
import os
from typing import List, Optional, Generator, Dict, Any
from pydriller import Commit
import repository_utils_core as core

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESOURCES_PATH = os.path.join(ROOT_PATH, "resources", "repositories")
RESULTS_PATH = os.path.join(ROOT_PATH, "results")
PLOTS_PATH = os.path.join(RESULTS_PATH, "plots")
LOGS_PATH = os.path.join(ROOT_PATH, "logs")

def create_directory(path: str):
    """
    Creates a directory at the specified path if it does not exist.
    @param path: The path of the directory to be created
    """
    os.makedirs(path, exist_ok=True)
    return path

def read_repository_names(language: str) -> List[str]:
    """
    Reads repository names from a file under 'resources/repositories/' and formats them
    as GitHub URLs from Apache (e.g., 'https://github.com/apache/{repo}.git').

    @param language: The programming language (e.g., "java", "kotlin").
    @return: A list of formatted GitHub repository URLs.
    """
    file_path = os.path.join(RESOURCES_PATH, f"{language}_repos.txt")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    with open(file_path, "r", encoding="utf-8") as file:
        return core.read_repository_names(file)


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
