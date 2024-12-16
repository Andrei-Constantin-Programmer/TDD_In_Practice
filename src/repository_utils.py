import os
from typing import List, Optional, Generator, Dict, Any
from pydriller import Commit
import repository_utils_core as core

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESOURCES_PATH = os.path.join(ROOT_PATH, "resources", "repositories")
RESULTS_PATH = os.path.join(ROOT_PATH, "results")

def create_resource_folder(name: str):
    path = os.path.join(RESULTS_PATH, name)
    os.makedirs(path, exist_ok=True)
    return path

def read_repository_names(language: str, count: Optional[int] = None) -> List[str]:
    """
    Reads repository names from a file under 'resources/repositories/' and formats them
    as GitHub URLs from Apache (e.g., 'https://github.com/apache/{repo}.git').

    Args:
        language (str): The programming language (e.g., "java", "kotlin").
        count (Optional[int]): The number of repos to read. If not provided, all repos are read.

    Returns:
        List[str]: A list of formatted GitHub repository URLs.
    """
    file_path = os.path.join(RESOURCES_PATH, f"{language}_repos.txt")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    with open(file_path, "r", encoding="utf-8") as file:
        return core.read_repository_names(file, count)


def read_csv(file_name: str) -> List[Dict[str, Any]]:
    """
    Reads a CSV file from the 'results/' directory and returns its content as a list of dictionaries.

    Args:
        file_name (str): The name of the CSV file (without the '.csv' extension).

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing rows in the CSV file.
    """
    file_path = os.path.join(RESULTS_PATH, f"{file_name}.csv")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    with open(file_path, "r", encoding="utf-8") as file:
        return core.read_csv(file)


def write_csv(content: List[List[Any]], file_name: str) -> None:
    """
    Writes content to a CSV file under 'results/'.

    Args:
        content (List[List[Any]]): Data to write to the CSV file, as a list of rows.
        file_name (str): The name of the CSV file.

    Returns:
        None
    """
    file_name = file_name if file_name.endswith(".csv") else f"{file_name}.csv"
    file_path: str = os.path.join(RESULTS_PATH, file_name)
    os.makedirs(RESULTS_PATH, exist_ok=True)

    with open(file_path, mode="w", encoding="utf-8", newline="") as file:
        core.write_csv(content, file)


def read_commits(repository_url: str) -> Generator[Commit, None, None]:
    """
    Reads commits from a repository using PyDriller.

    Args:
        repository_url (str): The URL of the repository.

    Returns:
        Generator[Commit, None, None]: A generator of Commit objects.
    """
    return core.read_commits(repository_url)