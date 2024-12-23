import os.path
import csv

def update_csv_data(file_path, data, headers, type_flag):
    '''
    Update the author's CSV file with the new information
    @param file_path: Path to the CSV file
    @param data: The data to be updated
    @param headers: The headers of the CSV file
    @param type_flag: Flag explaining what should be updated (either 'repo' or 'author')
    '''
    row_name = data[0]

    # If the CSV does not exist, create an empty CSV
    if not os.path.isfile(file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(headers)

    # Open the CSV and check if the repo/author already has a row in the CSV
    with open(file_path, 'r', newline='', encoding='utf-8') as csv_file:
        csv_data = list(csv.reader(csv_file))

    # Set a token to see if we can find the current repo/author in the CSV file
    found_row = False
    for row_index in range(0, len(csv_data)):
        if csv_data[row_index][0] == row_name:
            # We have found the repo/author in the CSV
            found_row = True
            if type_flag == 'repo':
                # Update the row in the CSV
                csv_data[row_index] = data
            if type_flag == 'author':
                # re calculate data and then update the row in the CSV
                pass

    if not found_row:
        # We have not found the repo/author
        # Create a new row in the CSV
        csv_data.append(data)

    # Write updated data back to the CSV
    with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(csv_data)


def update_author_count(commits, author_counts, test_files, index_to_update):
    '''
    Update all commit author's counts for a particular test file array
    @param commits: An Array containing CustomCommit objects
    @param author_counts: A map of authors to an array of commit types (before, after, during), each with the number of commits of that type for this author
    @param test_files: The test files to iterate over
    @index_to_update: The index of the commit type to update (before, after, during)
    '''
    for test_file in test_files:
        # for each test file, get the author
        author = str(commits[test_file[0]].author).split(',')[0]
        # check if the author is in the dictionary
        if author not in author_counts.keys():
            # the author is not in the dictionary, create the element
            author_counts[author] = [0, 0, 0]
        # now that the author is known to exist in the dictionary, increment the correct value
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
