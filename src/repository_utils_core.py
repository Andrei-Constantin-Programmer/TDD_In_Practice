import csv
from datetime import datetime
from typing import List, Generator, Optional, Dict, Any, IO
from pydriller import Repository as DrillerRepo, Commit
from models.Repository import Repository

def read_repositories(file_content: IO[str]) -> List[Repository]:
    lines = file_content.readlines()
    repositories: List[str] = [line.strip() for line in lines]
    return [Repository(repo_name, f"https://github.com/apache/{repo_name}.git") for repo_name in repositories]


def read_csv(file_content: IO[str]) -> List[Dict[str, Any]]:
    reader = csv.DictReader(file_content)
    return [row for row in reader]


def write_csv(content: List[List[Any]], file_obj: IO[str]) -> None:
    if not isinstance(content, list) or not all(isinstance(row, list) for row in content):
        raise ValueError("Content must be a list of lists.")
    
    writer = csv.writer(file_obj)
    writer.writerows(content)


def read_commits(repository_url: str, final_date: Optional[datetime] = None) -> Generator[Commit, None, None]:
    if final_date is not None and final_date > datetime.now():
        raise ValueError("Final date must be in the past.")
    to_date = final_date if final_date else datetime.now()
    return DrillerRepo(repository_url, only_modifications_with_file_types=['.java'], to=to_date).traverse_commits()