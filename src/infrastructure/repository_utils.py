from datetime import datetime
import os
from typing import List, Optional, Generator
from pydriller import Commit
from models.Repository import Repository
from pydriller import Repository as DrillerRepo, Commit
from infrastructure import file_utils

def read_repositories(language: str) -> List[Repository]:
    """
    Reads repository names from a file under 'resources/repositories/' and formats them
    as GitHub URLs from Apache (e.g., 'https://github.com/apache/{repo}.git').

    @param language: The programming language (e.g., "java", "kotlin").
    @return: A list of Repository objects.
    """
    file_path = os.path.join(file_utils.RESOURCES_PATH, f"{language}_repos.txt")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        repositories: List[str] = [line.strip() for line in lines]
        return [Repository(repo_name, f"https://github.com/apache/{repo_name}.git") for repo_name in repositories]

def read_commits(repository_url: str, final_date: Optional[datetime] = None) -> Generator[Commit, None, None]:
    """
    Reads commits from a repository using PyDriller.

    @param: repository_url: The URL of the repository.
    @param: final_date: Date to read commits up until from the given repository.

    @return: A generator of Commit objects.
    """
    if final_date is not None and final_date > datetime.now():
        raise ValueError("Final date must be in the past.")
    to_date = final_date if final_date else datetime.now()
    return DrillerRepo(repository_url, only_modifications_with_file_types=['.java'], to=to_date).traverse_commits()
