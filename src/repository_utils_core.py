import csv
from typing import List, Generator, Optional, Dict, Any, IO
from pydriller import Repository, Commit

def read_repository_names(file_content: IO[str], count: Optional[int] = None) -> List[str]:
    if count is not None and (not isinstance(count, int) or count <= 0):
        raise ValueError("Count must be a positive integer.")
    
    lines = file_content.readlines()
    repositories: List[str] = [line.strip() for line in lines[:count]] if count else [line.strip() for line in lines]
    return [f"https://github.com/apache/{repo}.git" for repo in repositories]


def read_csv(file_content: IO[str]) -> List[Dict[str, Any]]:
    reader = csv.DictReader(file_content)
    return [row for row in reader]


def write_csv(content: List[List[Any]], file_obj: IO[str]) -> None:
    if not isinstance(content, list) or not all(isinstance(row, list) for row in content):
        raise ValueError("Content must be a list of lists.")
    
    writer = csv.writer(file_obj)
    writer.writerows(content)

def read_commits(repository_url: str) -> Generator[Commit, None, None]:
    return Repository(repository_url).traverse_commits()