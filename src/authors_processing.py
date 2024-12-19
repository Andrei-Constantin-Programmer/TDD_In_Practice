from fileinput import close

import repository_utils
from models.JavaFileHandler import JavaFileHandler
import graphs
import commit_processing as process
import os.path, csv

def main():
    # Use repository_utils to get an array from the list of allowed repositories
    repositories = repository_utils.read_repository_names("java")[1:2]

    java_file_handler = JavaFileHandler()
    # For each repo on the list of allowed repositories
    for repo in repositories:
        commits, test_files = process.gather_commits_and_tests(repo, java_file_handler)
        commit_map = process.precompute_commit_map(commits)
        repo_name = repo.split("/")[-1].split(".")[0]

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

        # Output our results in the console
        print("\n")
        print("Test before Implementation: " + str(test_before))
        print("Test after Implementation: " + str(test_after))
        print("Test during Implementation: " + str(test_during))

        # Plot the bar graph using the function
        graphs.plot_bar_graph(test_before, test_during, test_after, repo_name)

        # Prepare data to write to the CSV
        data_for_repo_csv = [repo_name, 'java', test_before, test_after, test_during]
        repo_data_file_path = "../results/repo_data.csv"

        # If the CSV does not exist, create an empty CSV
        if not os.path.isfile(repo_data_file_path):
            with open(repo_data_file_path, 'w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["Repo Name", "Language", "Test Before", "Test After", "Test During"])

        # Open the CSV and check if the repo already has a row in the CSV
        with open(repo_data_file_path, 'r', newline='') as csv_file:
            csv_data = list(csv.reader(csv_file))

        # Set a token to see if we can find the current repo in the CSV file
        found_repo = False
        for row_index in range(0, len(csv_data)):
            if csv_data[row_index][0] == repo_name:
                # We have found the repo in the CSV
                found_repo = True
                # Update the row in the CSV
                csv_data[row_index] = data_for_repo_csv

        if not found_repo:
            # We have not found the repo
            # Create a new row in the CSV
            csv_data.append(data_for_repo_csv)

        # Write updated data back to the CSV
        with open(repo_data_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(csv_data)

main()

# WRITE AUTHOR SPECIFIC DATA TO THE AUTHORS CSV
# if author is already in the csv, update their values
# if author is not already in the csv, create new row for the author

'''
ONCE CSV WITH EVERYTHING (ONE CSV PER LANGUAGE)
WE CAN GENERATE THE GRAPHS FROM THE CSV FILE ON DEMAND
ROWS - REPO - LANGUAGE - ONE ROW FOR EACH METRIC

THIS MEANS WE MUST RETHINK HOW WE STORE AUTHOR INFORMATION - this is once csv for every single repo - 
updated over each repo

INFORMATION PER AUTHOR CAN BE DONE OVER MULTIPLE REPOSITORIES
RUN CODE ONCE WITHOUT LOOKING AT AUTHOR
RUN AUTHOR ANAYLSIS OVER COMPLETELY ANALYSED DATA AFTER TO GENERATE A 2nd CSV
'''


