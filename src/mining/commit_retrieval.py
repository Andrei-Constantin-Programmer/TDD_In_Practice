import asyncio
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

    commit_generator = repository_utils.read_commits(repo_url, final_date)
    if commit_generator is None:
        return []

    for commit in commit_generator:
        files = _retrieve_files(commit.modified_files, file_handler)
        commits.append(CustomCommit(commit.hash, files, commit.author, commit.author_date))

    return commits

def _get_serialized_file_name(repo_name: str):
    return os.path.join(file_utils.COMMITS_PATH, f"{repo_name}.pkl") 

async def retrieve_and_store_repo_info(repo: Repository, file_handler: LanguageFileHandler, final_date = None):
    """
    Retrieve, serialize, and write repository information to a file with the repo name under results/commits.
    @param repo: The URL to the repository.
    @param file_handler: Object containing information required to retrieve files specific to the a particular programming language
    """
    file_path = _get_serialized_file_name(repo.name)

    if file_utils.file_exists(file_path):
        return

    commits = await asyncio.to_thread(_retrieve_commits, repo.url, file_handler, final_date)
    if len(commits) == 0:
        return

    await asyncio.to_thread(serializer.serialize, file_path, commits)
    
def read_repo_info(repo_name: str):
    '''
    Reads repo information from a file.
    @param repo_name: The name of the repository.
    @return: An Array containing CustomCommit objects.
    '''
    file_path = _get_serialized_file_name(repo_name)
    return serializer.deserialize(file_path)