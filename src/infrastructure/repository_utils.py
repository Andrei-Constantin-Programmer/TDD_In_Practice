from datetime import datetime
import logging
import os
import re
from typing import List, Optional, Generator
from pydriller import Commit
from src.models.Repository import Repository
from pydriller import Repository as DrillerRepo, Commit
from src.infrastructure import file_utils

def read_repositories(language: str) -> List[Repository]:
    """
    Reads repository names from a file under 'resources/repositories/', removes duplicates,
    alphabetically orders them, and formats them as GitHub URLs from Apache
    (e.g., 'https://github.com/apache/{repo}.git'). 
    The updated list replaces the original file, with one repository per line.

    @param language: The programming language (e.g., "java", "kotlin").
    @return: A list of Repository objects.
    """
    file_path = os.path.join(file_utils.RESOURCES_PATH, f"{language}_repos.txt")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        repositories: List[str] = sorted(set(line.strip() for line in lines))

        with open(file_path, "w", encoding="utf-8") as file:
            file.write("\n".join(repositories))

        return [apache_repo_from_name(repo_name) for repo_name in repositories]

def read_commits(repository_url: str, file_extension: str, final_date: Optional[datetime] = None) -> Generator[Commit, None, None]:
    """
    Reads commits from a repository using PyDriller.

    @param: repository_url: The URL of the repository.
    @param: file_extension: The file extension to search for.
    @param: final_date: Date to read commits up until from the given repository.

    @return: A generator of Commit objects.
    """
    if final_date is not None and final_date > datetime.now():
        raise ValueError("Final date must be in the past.")
    to_date = final_date if final_date else datetime.now()
    
    return DrillerRepo(repository_url, only_modifications_with_file_types=[file_extension], to=to_date).traverse_commits()

def repo_from_url(repo_url: str):
    repo_name = re.search(r"github\.com/[^/]+/([^/.]+)", repo_url).group(1) if re.search(r"github\.com/[^/]+/([^/.]+)", repo_url) else None

    if repo_name is None:
        raise ValueError(f"Invalid repository URL '{repo_url}'")

    return Repository(repo_name, repo_url)

def apache_repo_from_name(repo_name: str):
    repo_url = f"https://github.com/apache/{repo_name}.git"
    return Repository(repo_name, repo_url)