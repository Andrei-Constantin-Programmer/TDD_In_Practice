from fileinput import close

import repository_utils
from models.JavaFileHandler import JavaFileHandler
import graphs
import commit_processing as process
import os.path, csv, timeit, tqdm

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



def main():
    # initial setup
    # ../results/author_data.csv needs to be deleted if it already exists
    if os.path.isfile('../results/author_data.csv'):
        os.remove('../results/author_data.csv')

    # Use repository_utils to get an array from the list of allowed repositories
    repositories = repository_utils.read_repository_names("java")

    java_file_handler = JavaFileHandler()
    # For each repo on the list of allowed repositories
    timed_list = tqdm.tqdm(repositories)
    for repo in timed_list:
        # Initialise a timer
        start_time = timeit.default_timer()
        # get repo name
        repo_name = repo.split("/")[-1].split(".")[0]
        # set progress bar message
        timed_list.set_description('Processing ' + repo_name)
        # gather data
        commits, test_files = process.gather_commits_and_tests(repo, java_file_handler)
        # preprocess commits
        commit_map = process.precompute_commit_map(commits)

        # Initialize Counters
        test_after = 0
        test_before = 0
        test_during = 0
        array_after = []
        array_before = []
        array_during = []

        # Iterate over each test file tuple and assess whether tests are committed before, after or during the implementation files
        for test_file in test_files:
            nearest_implementation = process.find_nearest_implementation(test_file, commits, commit_map, java_file_handler)
            if nearest_implementation is not None:
                if test_file[0] < nearest_implementation:
                    # Test was committed before the implementation
                    test_before += 1
                    array_before.append(test_file)
                if test_file[0] > nearest_implementation:
                    # Test was committed after the implementation
                    test_after += 1
                    array_after.append(test_file)
                if test_file[0] == nearest_implementation:
                    # Test was committed in the same commit as the implementation
                    test_during += 1
                    array_during.append(test_file)

        duration = round((timeit.default_timer() - start_time), 1)
        avg_size_before = calculate_average_commit_size(commits, array_before)
        avg_size_after = calculate_average_commit_size(commits, array_after)
        avg_size_during = calculate_average_commit_size(commits, array_during)
        avg_size_total = round((avg_size_before + avg_size_after + avg_size_during)/3, 1)

        # Output our results in the console
        print("\n")
        print("Completed Running on " + repo_name + " in " + str(duration) + " seconds")
        print("Test before Implementation: " + str(test_before))
        print("Test after Implementation: " + str(test_after))
        print("Test during Implementation: " + str(test_during))

        # Plot the bar graph using the function
        #graphs.plot_bar_graph(test_before, test_during, test_after, repo_name)

        # Prepare data to write to the repo CSV
        repo_headers = ["Repo Name", "Language", "Test Before", "Test After", "Test During", "Duration (s)",
                        "Avg Before Commit Size", "Avg After Commit Size", "Avg During Commit Size", "Avg Commit Size"]
        repo_data_file_path = "../results/repo_data.csv"
        data_for_repo_csv = [repo_name, 'java', test_before, test_after, test_during, duration,
                             avg_size_before, avg_size_after, avg_size_during, avg_size_total]
        update_csv_data(repo_data_file_path, data_for_repo_csv, repo_headers, 'repo')

        # Prepare data to write to the author CSV
        author_headers = ["Author", "Test Before", "Test After", "Test During"]
        author_data_file_path = "../results/author_data.csv"

        # calculate the counts for each author
        # dictionary key:authors name, element:[test_before, test_after, test_during]
        author_counts = {}
        update_author_count(commits, author_counts, array_before, 0)
        update_author_count(commits, author_counts, array_after, 1)
        update_author_count(commits, author_counts, array_during, 2)

        #file_path, data, headers, type_flag
        for key in author_counts.keys():
            update_csv_data(author_data_file_path, [key] + author_counts[key], author_headers, 'author')


main()

# WRITE AUTHOR SPECIFIC DATA TO THE AUTHORS CSV
# if author is already in the csv, update their values
# if author is not already in the csv, create new row for the author

'''
WORK ON METHODOLOGY OF REPORT


ADD STORAGE OF AVERAGE COMMIT, BEFORE, AFTER, DURING and ALL into this CSV
Caluclate this from the 3 arrays above
Units = number of files


INFORMATION PER AUTHOR CAN BE DONE OVER MULTIPLE REPOSITORIES
RUN CODE ONCE WITHOUT LOOKING AT AUTHOR
RUN AUTHOR ANALYSIS OVER COMPLETELY ANALYSED DATA AFTER TO GENERATE A 2nd CSV
'''


