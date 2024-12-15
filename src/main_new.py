from pydriller import Repository
import repository_utils

class CustomCommit:
    def __init__(self, commit_hash, modified_files, author, date):
        self.commit_hash = commit_hash
        self.modified_files = modified_files
        self.author = author
        self.date = date

    def __str__(self):
        return ("\nCOMMIT - " + self.commit_hash +
                "\nMODIFIED - " + str(self.modified_files) +
                "\nAUTHOR - " + str(self.author) +
                "\nDATE - " + str(self.date) + "\n")

def retrieve_files(modified_files):
    """
    Function to take a modified_files attribute from a Pydriller Commit object and return a simple array of Filenames
    modified_files: array from Commit.modified_files from Pydriller, contains file objects.
    """
    # Initialise an empty list to store filenames
    files = []
    # Iterate through all file objects from the Pydriller modified_files passed in
    for file in modified_files:
        if "Test" in file.filename:
            # If the filename has "Test" in it, then append the filename to the files array
            files.append(file.filename)
    # Return the files array
    return files

def retrieve_commits(repo):
    """
    Function to take a repo name and convert commits into a "CustomCommit" object.
    Repo: A String representing the repository name to search and retrieve commits from
    """
    # Initialize an empty list to store commits
    commits = []

    # Iterate through all the commits from the specified Repo
    for commit in repository_utils.read_commits(repo):
        # Retrieve an array of filenames for the commit
        files = retrieve_files(commit.modified_files)
        # Append a CustomCommit object to the commits array
        commits.append(CustomCommit(commit.hash, files, commit.author, commit.author_date))
    # Return the array
    return commits

def find_nearest_after():
    '''
    Function to take a file and its commit hash and find the next commit in the future
    which has a corresponding implementation file
    '''
    pass

def find_nearest_before():
    pass

def main():
    # Use repository_utils to get an array from the list of allowed repositories
    repositories = repository_utils.read_repository_names("java")[1:2]

    # For each repo on the list of allowed repositories
    for repo in repositories:
        # Get the commits or the repo this is an array of CustomCommit objects
        commits = retrieve_commits(repo)

        # For each test file, create a tuple with the filename and its index in the commits array
        test_files = []
        for i in range(0, len(commits)):
            for file in commits[i].modified_files:
                test_files.append((i, file))

        # Output Some Data
        # The array "commits" stores all the commits and the details for each commit, the elements are CustomCommit objects
        print(commits[0])
        # The array "test_files" is an array of test files and the index that the files commit is in the "commits" array
        print(test_files)

        '''
        to search for the nearest commit we first take a test file from the test_files array
        we then strip tests from the string
        
        we then search the commits after and before the commit separately to find a commit with the relevant implementation file
        
        the same test file can occur multiple times in the test_files array so we must take this into account
          
        '''

main()
