from datetime import datetime
import repository_utils
from models.JavaFileHandler import JavaFileHandler
import graphs
import commit_processing as process

date_of_experiment = datetime(2024, 12, 1, 0, 0, 0)

def main():
    # Use repository_utils to get an array from the list of allowed repositories
    repositories = repository_utils.read_repository_names("java")[0:2]

    java_file_handler = JavaFileHandler()
    # For each repo on the list of allowed repositories
    for repo in repositories:
        commits, test_files = process.gather_commits_and_tests(repo, java_file_handler, final_date=date_of_experiment)
        commit_map = process.precompute_commit_map(commits)

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
            nearest_implementation = process.find_nearest_implementation(test_file, commits, commit_map, java_file_handler)
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