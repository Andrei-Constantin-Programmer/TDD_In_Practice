import asyncio
import logging
import os
from src.infrastructure import repository_utils as repository_utils
from src.infrastructure import file_utils as file_utils
from src.infrastructure import serialize as serializer
from src.models.LanguageFileHandler import LanguageFileHandler
from src.models.CustomCommit import CustomCommit
from src.models.Repository import Repository

def _retrieve_files(modified_files, file_handler: LanguageFileHandler):
    files = []

    for file in modified_files:
        if file_handler.file_extension in file.filename:
            files.append(file.filename)

    return files

def _retrieve_commits(repo_url, file_handler: LanguageFileHandler, final_date = None):
    commits = []

    try:
        for commit in repository_utils.read_commits(repo_url, file_handler.file_extension, final_date):
            files = _retrieve_files(commit.modified_files, file_handler)
            commits.append(CustomCommit(commit.hash, files, commit.author, commit.author_date))
    except Exception as e:
        logging.error(f"Could not drill repository {repo_url}: {e}")
        return []

    return commits

def _get_serialized_file_name(repo_name: str):
    return os.path.join(file_utils.COMMITS_PATH, f"{repo_name}.pkl") 

async def retrieve_and_store_repo_info(repo: Repository, file_handler: LanguageFileHandler, final_date = None, force_mine: bool = False):
    """
    Retrieve, serialize, and write repository information to a file with the repo name under results/commits.
    @param repo: The URL to the repository.
    @param file_handler: Object containing information required to retrieve files specific to the a particular programming language
    """
    file_path = _get_serialized_file_name(repo.name)

    if not force_mine and file_utils.file_exists(file_path):
        return

    commits = await asyncio.to_thread(_retrieve_commits, repo.url, file_handler, final_date)
    if len(commits) == 0:
        return

    await asyncio.to_thread(serializer.serialize, file_path, commits)
    
def read_repo_info(repo_name: str):
    '''
    Reads repo information from a file.
    @param repo_name: The name of the repository.
    @return: An Array containing CustomCommit objects, or None if the deserialization fails.
    '''
    file_path = _get_serialized_file_name(repo_name)
    try:
        repo_info = serializer.deserialize(file_path)
    except Exception as e:
        logging.warning(f"No 'commits' file found for repository '{repo_name}': {e}")
        return []
    return repo_info