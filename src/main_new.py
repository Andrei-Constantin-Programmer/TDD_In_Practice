from pydriller import Repository
import repository_utils

def main():
    repositories = repository_utils.read_repository_names("java")[1:2]

    for repo in repositories:
        print("Running on " + repo.split('/')[-1].strip('.git') + '\n')

        # Loop though all commits and create an array of tuples
        # The tuples store all the test files and their corresponding commits
        # If a test file appears in multiple commits, we store multiple tuples with the same commit

        test_files = []

        # For each commit
        for counter, commit in enumerate(repository_utils.read_commits(repo)):
            # Look through each file in the commit
            for file in commit.modified_files:
                # Identify test files
                if "Test" in file.filename:
                    test_files.append((counter, file.filename, commit.hash))

        print("DONE")
        for tuple in test_files:
            print(tuple)

main()
