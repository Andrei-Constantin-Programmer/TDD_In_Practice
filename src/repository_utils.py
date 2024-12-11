import os
import csv
from typing import List, Optional, Generator, Dict, Any
from pydriller import Repository, Commit

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESOURCES_PATH = os.path.join(ROOT_PATH, "resources", "repositories")
RESULTS_PATH = os.path.join(ROOT_PATH, "results")

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
    file_path: str = os.path.join(RESOURCES_PATH, f"{language}_repos.txt")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    
    if count is not None and (not isinstance(count, int) or count <= 0):
        raise ValueError("Count must be a positive integer.")
    
    with open(file_path, "r", encoding="utf-8") as file:
        lines: List[str] = file.readlines()
    
    repositories: List[str] = [line.strip() for line in lines[:count]] if count else [line.strip() for line in lines]
    return [f"https://github.com/apache/{repo}.git" for repo in repositories]


def read_commits(repository_url: str) -> Generator[Commit, None, None]:
    """
    Reads commits from a repository using PyDriller.

    Args:
        repository_url (str): The URL of the repository.

    Returns:
        Generator[Commit, None, None]: A generator of Commit objects.
    """
    return Repository(repository_url).traverse_commits()


def read_csv(file_name: str) -> List[Dict[str, Any]]:
    """
    Reads a CSV file from the 'results/' directory and returns its content as a list of dictionaries.

    Args:
        file_name (str): The name of the CSV file (without the '.csv' extension).

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing rows in the CSV file.
    """
    if not isinstance(file_name, str):
        raise ValueError("File name must be a string.")
    
    file_path: str = os.path.join(RESULTS_PATH, f"{file_name}.csv")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        content: List[Dict[str, Any]] = [row for row in reader]
    
    return content


def write_csv(content: List[List[Any]], file_name: str) -> None:
    """
    Writes content to a CSV file under 'results/'.

    Args:
        content (List[List[Any]]): Data to write to the CSV file, as a list of rows.
        file_name (str): The name of the CSV file.

    Returns:
        None
    """
    if not isinstance(content, list) or not all(isinstance(row, list) for row in content):
        raise ValueError("Content must be a list of lists.")
    if not isinstance(file_name, str):
        raise ValueError("File name must be a string.")
    
    file_name = file_name if file_name.endswith(".csv") else f"{file_name}.csv"
    file_path: str = os.path.join(RESULTS_PATH, file_name)
    
    os.makedirs(RESULTS_PATH, exist_ok=True)
    
    with open(file_path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(content)
