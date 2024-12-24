import logging
import os.path
import repository_utils

repo_headers = ["Repo Name", "Language", "Test Before", "Test After", "Test During", "Duration (s)", 
                "Avg Before Commit Size", "Avg After Commit Size", "Avg During Commit Size", "Avg Commit Size"]

author_headers = ["ID", "Author", "Test Before", "Test After", "Test During"]

def update_author_data(data: list[str]):
    """
    Update the author's CSV file with new data
    @param data: The data to update the file with
    """
    file = os.path.join(repository_utils.RESULTS_PATH, "author_data.csv")
    row_name = data[0]
    author_update_function = lambda data: data
    repository_utils.create_or_update_csv(file, author_headers, data, row_name, author_update_function)
    logging.notify("Wrote author data to " + file)

def update_repo_data(data: list[str]):
    """
    Update the repo CSV with the new data
    @param data: The data to update the file with
    """
    file = os.path.join(repository_utils.RESULTS_PATH, "repo_data.csv")
    row_name = data[0]
    repository_utils.create_or_update_csv(file, repo_headers, data, row_name)
    logging.notify("Wrote repo data to " + file)

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

def calculate_average_commit_size(commits, test_files):
    '''
    Calculate the average commit size for commits containing tests
    @param commits: An Array containing CustomCommit objects
    @param test_files: The test files to iterate over
    @return: The average commit size
    '''
    total = 0
    counter = 0
    complete_indexes = []

    for test_file in test_files:
        if test_file[0] not in complete_indexes:
            total += commits[test_file[0]].size
            counter += 1
            complete_indexes.append(test_file[0])

    return round(total/counter, 1)
