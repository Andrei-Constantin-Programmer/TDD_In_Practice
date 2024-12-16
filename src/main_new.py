from collections import defaultdict
import repository_utils
from models.CustomCommit import CustomCommit
from models.JavaFileHandler import JavaFileHandler
from models.LanguageFileHandler import LanguageFileHandler
import graphs

def retrieve_files(modified_files, file_handler: LanguageFileHandler):
    """
    Function to take the 'modified_files' attribute of a Pydriller Commit object and return a simple array of filename strings
    @param modified_files: An array of ModifiedFile objects taken from the Commit object of pydriller
    @return: An array of filename strings
    """
    # Initialise an empty list to store filenames
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
    @return: An Array containing CustomCommit objects, one CustomCommit object is appended per commit
    """
    # Initialize an empty list to store commits
    commits = []

    # Iterate through all the commits from the specified Repo
    for commit in repository_utils.read_commits(repo):
        # Retrieve an array of filenames for the commit
        files = retrieve_files(commit.modified_files, file_handler)
        # Append a CustomCommit object to the commits array
        commits.append(CustomCommit(commit.hash, files, commit.author, commit.author_date))

    # Return the array
    return commits


def gather_commits_and_tests(repo, file_handler: LanguageFileHandler):
    """
    Retrieve Commits from GitHub using the retrieve_commits, and analyse tests to produce a test_files array
    @param repo: A String representing the repository which we will search and retrieve commits from
    @return: An Array containing CustomCommit objects, one CustomCommit object is appended per commit
    @return: An Array containing Tuples holding the tests file name and the index in 'Commits' it can be found at
    """
    # Get the commits of the repo this is an array of CustomCommit objects
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
    @param commits: An Array containing CustomCommit objects with one CustomCommit object per commit
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


def main():
    # Use repository_utils to get an array from the list of allowed repositories
    repositories = repository_utils.read_repository_names("java")[1:2]

    java_file_handler = JavaFileHandler()
    # For each repo on the list of allowed repositories
    for repo in repositories:
        commits, test_files = gather_commits_and_tests(repo, java_file_handler)
        commit_map = precompute_commit_map(commits)

        # Output Some Data
        # The array "commits" stores all the commits and the details for each commit, the elements are CustomCommit objects
        print(commits[0])
        # The array "test_files" is an array of test files and the index that the files commit is in the "commits" array
        print("Length of test_files: " + str(len(test_files)))
        print(test_files)

        # Initialize Counters
        test_after = 0
        test_before = 0
        test_during = 0

        # Iterate over each test file tuple and assess whether tests are committed before, after or during the implementation files
        for test_file in test_files:
            nearest_implementation = find_nearest_implementation(test_file, commits, commit_map, java_file_handler)
            if nearest_implementation is not None:
                if test_file[0] < nearest_implementation:
                    # Test was committed before the implementation
                    test_before += 1
                if test_file[0] > nearest_implementation:
                    # Test was committed after the implementation
                    test_after += 1
                if test_file[0] == nearest_implementation:
                    # Test was committed in the same commit as the implementation
                    test_during += 1

        # Output our results in the console
        print("\n")
        print("Test before Implementation: " + str(test_before))
        print("Test after Implementation: " + str(test_after))
        print("Test during Implementation: " + str(test_during))

        # Plot the bar graph using the function
        graphs.plot_bar_graph(test_before, test_during, test_after, repo.split("/")[-1].split(".")[0])


main()