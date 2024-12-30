import logging
import os.path
from src.infrastructure import file_utils

AUTHOR_FILE_NAME = "author_data"
AUTHOR_CSV_PATH = os.path.join(file_utils.RESULTS_PATH, f"{AUTHOR_FILE_NAME}.csv")
REPO_CSV_PATH = os.path.join(file_utils.RESULTS_PATH, "repo_data.csv")

REPO_HEADER = ["Repo Name", "Language", "Test Before", "Test After", "Test During", "Duration (s)", 
                "Avg Before Commit Size", "Avg After Commit Size", "Avg During Commit Size", "Avg Commit Size"]

AUTHOR_HEADER = ["Author", "Test Before", "Test After", "Test During"]

def _update_author_data_from_csv_line(data: list[str], csv_data: list[str]):
    if len(data) != len(csv_data):
        raise IndexError("Author data and CSV author data don't match!")
    
    updated_data = [str(int(data[i]) + int(csv_data[i])) for i in range (1, len(data))]
    return [data[0]] + updated_data

def update_author_data(data: list[str]):
    """
    Update the author's CSV file with new data
    @param data: The data to update the file with
    """
    author_name = data[0]
    author_update_function = lambda data, csv_data: _update_author_data_from_csv_line(data, csv_data)
    file_utils.create_or_update_csv(AUTHOR_CSV_PATH, AUTHOR_HEADER, data, author_name, author_update_function)
    logging.notify("Wrote author data to " + AUTHOR_CSV_PATH)

def update_repo_data(data: list[str]):
    """
    Update the repo CSV with the new data
    @param data: The data to update the file with
    """
    repo_name = data[0]
    file_utils.create_or_update_csv(REPO_CSV_PATH, REPO_HEADER, data, repo_name)
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

def anonymyse_authors():
    '''
    Update the author CSV file to replace author names with numeric values
    '''
    author_data = file_utils.read_csv(AUTHOR_FILE_NAME)
    if len(author_data) == 0:
        return

    header = list(author_data[0].keys())

    updated_data = [header]
    for index, row in enumerate(author_data, start=1):
        updated_row = row.copy()
        updated_row["Author"] = str(index)
        updated_data.append(list(updated_row.values()))

    file_utils.write_csv(updated_data, AUTHOR_FILE_NAME)
    logging.notify("Anonymized author data.")
