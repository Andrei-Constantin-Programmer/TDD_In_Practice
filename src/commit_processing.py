from collections import defaultdict
import repository_utils
from models.CustomCommit import CustomCommit
from models.LanguageFileHandler import LanguageFileHandler

def retrieve_files(modified_files, file_handler: LanguageFileHandler):
    """
    Function to take the 'modified_files' attribute of a Pydriller Commit object and return a simple array of filename strings
    @param modified_files: An array of ModifiedFile objects taken from the Commit object of pydriller
    @param file_handler: Object containing the extension of a particular programming language
    @return: An array of filename strings
    """
    files = []

    # Iterate through all file objects from the Pydriller modified_files passed in
    for file in modified_files:
        if file_handler.file_extension in file.filename:
            files.append(file.filename)

    return files


def retrieve_commits(repo, file_handler: LanguageFileHandler):
    """
    Function to take a repo name and convert commits into a "CustomCommit" object.
    @param repo: A String representing the repository which we will search and retrieve commits from
    @param file_handler: Object containing information required to retrieve files specific to the a particular programming language
    @return: An Array containing CustomCommit objects, one CustomCommit object is appended per commit
    """
    commits = []

    for commit in repository_utils.read_commits(repo):
        files = retrieve_files(commit.modified_files, file_handler)
        commits.append(CustomCommit(commit.hash, files, commit.author, commit.author_date))

    # Return the array
    return commits


def gather_commits_and_tests(repo, file_handler: LanguageFileHandler):
    """
    Retrieve Commits from GitHub using the retrieve_commits, and analyse tests to produce a test_files array
    @param repo: A String representing the repository which we will search and retrieve commits from
    @param file_handler: Object containing information required to retrieve commits that modify files of a particular programming language
    @return: A tuple containing an Array with CustomCommit objects and an Array of tuples of the form (test file name, commit index)
    """
    commits = retrieve_commits(repo, file_handler)

    # For each test file, create a tuple with the filename and its index in the commits array
    test_files = []
    for i in range(0, len(commits)):
        for file in commits[i].modified_files:
            if file_handler.is_test_file(file):
                test_files.append((i, file))

    return commits, test_files


def precompute_commit_map(commits):
    """
    Precompute a mapping from filenames to their commit indices.
    @param commits: An Array containing CustomCommit objects
    @return: A map of files to commit indexes where they are modified
    """
    file_to_commit_map = defaultdict(list)
    for i, commit in enumerate(commits):
        for file in commit.modified_files:
            file_to_commit_map[file].append(i)
    return file_to_commit_map


def find_nearest_implementation(test_file, commits, commit_map, file_handler: LanguageFileHandler):
    """
    Function to take a test_file tuple and list of commits and find the nearest commit taking before and after into account
    @param test_file: A Tuple holding the tests file name and the index in 'Commits' it can be found
    @param commits: An Array containing CustomCommit objects
    @param commit_map: A map of files to commit indexes where they are modified
    @return: Integer index where the tests nearest implementation file is (only searching future commits) or None.
    """
    implementation_file = file_handler.get_implementation_file(test_file[1])

    candidate_indices = commit_map.get(implementation_file, [])
    if not candidate_indices:
        return None
    
    test_index = test_file[0]
    before_candidates = [i for i in candidate_indices if i < test_index]
    after_candidates = [i for i in candidate_indices if i >= test_index]

    before_index = max(before_candidates, default=None)
    after_index = min(after_candidates, default=None)

    if after_index == before_index:
        return after_index
    if after_index is None:
        return before_index
    if before_index is None:
        return after_index

    distance_before = commits[test_index].date - commits[before_index].date
    distance_after = commits[after_index].date - commits[test_index].date

    return before_index if distance_before <= distance_after else after_index
