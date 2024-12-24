from datetime import datetime
import logging
import os
import timeit
from tqdm import tqdm
import repository_utils
from models.JavaFileHandler import JavaFileHandler
import commit_processing as process
import configuration
from csv_export import calculate_average_commit_size, update_author_count, update_author_data, update_repo_data

date_of_experiment = datetime(2024, 12, 1, 0, 0, 0)

def main():
    logging.notify("Program 'main()' has started")
    
    # Use repository_utils to get an array from the list of allowed repositories
    repositories = repository_utils.read_repository_names("java")[0:1]
    timed_list = tqdm(repositories)

    java_file_handler = JavaFileHandler()
    # For each repo on the list of allowed repositories
    for repo in timed_list:
        repo_name = repo.split("/")[-1].split(".")[0]

        timed_list.set_description('Started processing ' + repo_name)
        logging.notify("Started processing " + repo_name)
        start_time = timeit.default_timer()

        commits, test_files = process.gather_commits_and_tests(repo, java_file_handler, final_date=date_of_experiment)
        commit_map = process.precompute_commit_map(commits)

        array_before = []
        array_after = []
        array_during = []

        # Iterate over each test file tuple and assess whether tests are committed before, after or during the implementation files
        for test_file in test_files:
            nearest_implementation = process.find_nearest_implementation(test_file, commits, commit_map, java_file_handler)
            if nearest_implementation is not None:
                if test_file[0] < nearest_implementation:
                    # Test was committed before the implementation
                    array_before.append(test_file)
                if test_file[0] > nearest_implementation:
                    # Test was committed after the implementation
                    array_after.append(test_file)
                if test_file[0] == nearest_implementation:
                    # Test was committed in the same commit as the implementation
                    array_during.append(test_file)

        duration = round((timeit.default_timer() - start_time), 1)
        avg_size_before = calculate_average_commit_size(commits, array_before)
        avg_size_after = calculate_average_commit_size(commits, array_after)
        avg_size_during = calculate_average_commit_size(commits, array_during)
        avg_size_total = round((avg_size_before + avg_size_after + avg_size_during)/3, 1)

        logging.notify("Iteration over " + repo_name + "has completed")

        test_before = len(array_before)
        test_after = len(array_after)
        test_during = len(array_during)
        data_for_repo_csv = [repo_name, 'java', test_before, test_after, test_during, duration,
                             avg_size_before, avg_size_after, avg_size_during, avg_size_total]
        
        update_repo_data(data_for_repo_csv)

        author_counts = {}
        update_author_count(commits, author_counts, array_before, 0)
        update_author_count(commits, author_counts, array_after, 1)
        update_author_count(commits, author_counts, array_during, 2)

        for key in author_counts.keys():
            update_author_data([key] + author_counts[key])

        processing_finished_message = "Finished processing " + repo_name
        logging.notify(processing_finished_message)
        print(processing_finished_message)

configuration.setup_directories()
configuration.setup_logging()

main()