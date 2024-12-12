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
        commits = [commit for commit in repository_utils.read_commits(repo)]

        # For each commit
        for commit_number in range(0, len(commits)-1):
            # Look through each file in the commit
            for file in commits[commit_number].modified_files:
                # Identify test files
                if "Test" in file.filename:
                    test_files.append((file.filename, commits[commit_number].hash, commit_number))

        print("DONE")

main()
