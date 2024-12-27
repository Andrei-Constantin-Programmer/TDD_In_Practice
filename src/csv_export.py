import logging
import os.path
import repository_utils

AUTHOR_CSV_PATH = os.path.join(repository_utils.RESULTS_PATH, "author_data.csv")
REPO_CSV_PATH = os.path.join(repository_utils.RESULTS_PATH, "repo_data.csv")

repo_headers = ["Repo Name", "Language", "Test Before", "Test After", "Test During", "Duration (s)", 
                "Avg Before Commit Size", "Avg After Commit Size", "Avg During Commit Size", "Avg Commit Size"]

author_headers = ["ID", "Author", "Test Before", "Test After", "Test During"]

def update_author_data(data: list[str]):
    """
    Update the author's CSV file with new data
    @param data: The data to update the file with
    """
    author_name = data[0]
    author_update_function = lambda data: data
    repository_utils.create_or_update_csv(AUTHOR_CSV_PATH, author_headers, data, author_name, author_update_function)
    logging.notify("Wrote author data to " + AUTHOR_CSV_PATH)

def update_repo_data(data: list[str]):
    """
    Update the repo CSV with the new data
    @param data: The data to update the file with
    """
    repo_name = data[0]
    repository_utils.create_or_update_csv(REPO_CSV_PATH, repo_headers, data, repo_name)
    logging.notify("Wrote repo data to " + REPO_CSV_PATH)

def update_author_count(commits, author_counts, test_files, index_to_update):
    '''
    Update all commit author's counts for a particular test file array
    @param commits: An Array containing CustomCommit objects
    @param author_counts: A map of authors to an array of commit types (before, after, during), each with the number of commits of that type for this author
    @param test_files: The test files to iterate over
    @index_to_update: The index of the commit type to update (before, after, during)
    '''
    for test_file in test_files:
        author = str(commits[test_file[0]].author).split(',')[0]
        if author not in author_counts.keys():
            author_counts[author] = [0, 0, 0]
        author_counts[author][index_to_update] += 1
