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
        commits = []
        for commit in repository_utils.read_commits(repo):
            files = []
            for file in commit.modified_files:
                if "Test" in file.filename:
                    files.append(file.filename)
            commits.append(CustomCommit(commit.hash, files, commit.author, commit.author_date))

        test_files = []
        for i in range(0, len(commits)):
            for file in commits[i].modified_files:
                test_files.append((i, file))

        print(test_files)

main()
