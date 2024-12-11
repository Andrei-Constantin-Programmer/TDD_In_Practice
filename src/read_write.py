import os
import csv
from pydriller import Repository

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESOURCES_PATH = os.path.join(ROOT_PATH, "resources", "repositories")
RESULTS_PATH = os.path.join(ROOT_PATH, "results")

def read_repository_names(language, count=None):
    file_path = os.path.join(RESOURCES_PATH, f"{language}_repos.txt")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    
    if count is not None and (not isinstance(count, int) or count <= 0):
        raise ValueError("Count must be a positive integer.")
    
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    repositories = [line.strip() for line in lines[:count]] if count else [line.strip() for line in lines]
    return [f"https://github.com/apache/{repo}.git" for repo in repositories]

def read_commits(repository_url):
    return Repository(repository_url).traverse_commits()

def read_csv(file_name):
    if not isinstance(file_name, str):
        raise ValueError("File name must be a string.")
    
    file_path = os.path.join(RESULTS_PATH, f"{file_name}.csv")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        content = [row for row in reader]
    
    return content

def write_csv(content, file_name):
    if not isinstance(content, list) or not all(isinstance(row, list) for row in content):
        raise ValueError("Content must be a list of lists.")
    if not isinstance(file_name, str):
        raise ValueError("File name must be a string.")
    
    file_path = os.path.join(RESULTS_PATH, f"{file_name}.csv")
    
    os.makedirs(RESULTS_PATH, exist_ok=True)
    
    with open(file_path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(content)
