from pydriller import Repository
import repository_utils

class CustomCommit:
    def __init__(self, commit_hash, modified_files, author, date):
        self.commit_hash = commit_hash
        self.modified_files = modified_files
        self.author = author
        self.date = date

    def __str__(self):
        print("\n")
        print("COMMIT - " + self.commit_hash)
        print("MODIFIED - " + str(self.modified_files))
        print("AUTHOR - " + str(self.author))
        print("DATE - " + str(self.date))
        return ""


def main():

    repositories = repository_utils.read_repository_names("java")[1:2]

    for repo in repositories:
        my_list = []
        for commit in repository_utils.read_commits(repo):
            files = []
            for file in commit.modified_files:
                if "Test" in file.filename:
                    files.append(file.filename)
            my_list.append(CustomCommit(commit.hash, files, commit.author, commit.author_date))

        print(my_list[0])

    quit()
    #######

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
