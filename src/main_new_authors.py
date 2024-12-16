from pydriller import Repository
import repository_utils
import matplotlib.pyplot as plt

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
    Function to take the 'modified_files' attribute of a Pydriller Commit object and return a simple array of filename strings
    @param modified_files: An array of ModifiedFile objects taken from the Commit object of pydriller
    @return: An array of filename strings
    """
    # Initialise an empty list to store filenames
    files = []

    # Iterate through all file objects from the Pydriller modified_files passed in
    for file in modified_files:
        if ".java" in file.filename:
            # If the filename has ".java" in it, then append the file name to the files array
            files.append(file.filename)

    # Return the files array
    return files

def retrieve_commits(repo):
    """
    Function to take a repo name and convert commits into a "CustomCommit" object.
    @param repo: A String representing the repository which we will search and retrieve commits from
    @return: An Array containing CustomCommit objects, one CustomCommit object is appended per commit
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


def gather_commits_and_tests(repo):
    """
    Retrieve Commits from GitHub using the retrieve_commits, and analyse tests to produce a test_files array
    @param repo: A String representing the repository which we will search and retrieve commits from
    @return: An Array containing CustomCommit objects, one CustomCommit object is appended per commit
    @return: An Array containing Tuples holding the tests file name and the index in 'Commits' it can be found at
    """
    # Get the commits of the repo this is an array of CustomCommit objects
    commits = retrieve_commits(repo)

    # For each test file, create a tuple with the filename and its index in the commits array
    test_files = []
    for i in range(0, len(commits)):
        for file in commits[i].modified_files:
            if "Test" in file:
                test_files.append((i, file))

    return commits, test_files


def find_nearest_after(test_file, commits):
    """
    Function to take a 'test_file' tuple and list of CustomCommit objects and find the nearest commit in the FUTURE
    containing the corresponding implementation filename
    @param test_file: A Tuple holding the tests file name and the index in 'Commits' it can be found
    @param commits: An Array containing CustomCommit objects with one CustomCommit object per commit
    @return: Integer index where the tests nearest implementation file is (only searching future commits) or None.
    """
    # Strip 'Tests' or 'Test' from the test file's filename
    implementation_file_name = test_file[1].replace("Tests", "").replace("Test", "")

    # Look through every commit including or AFTER the commit that committed the test file working forwards
    for i in range(test_file[0], len(commits)):
        # Check if the implementation file is in the commit
        if implementation_file_name in commits[i].modified_files:
            # Return the index where the implementation file was found
            return i
    # If we get here, no implementation file was found, so return None
    return None


def find_nearest_before(test_file, commits):
    """
    Function to take a 'test_file' tuple and list of CustomCommit objects and find the nearest commit in the PAST
    containing the corresponding implementation filename
    @param test_file: A Tuple holding the tests file name and the index in 'Commits' it can be found
    @param commits: An Array containing CustomCommit objects with one CustomCommit object per commit
    @return: Integer index where the tests nearest implementation file is (only searching past commits) or None.
    """
    # Strip 'Tests' or 'Test' from the test file's filename
    implementation_file_name = test_file[1].replace("Tests", "").replace("Test", "")

    # Look through every commit including or BEFORE the commit that committed the test file working backwards
    for i in range(test_file[0], -1, -1):
        # Check if the implementation file is in the commit
        if implementation_file_name in commits[i].modified_files:
            # Return the index where the implementation file was found
            return i
    # If we get here, no implementation file was found, so return None
    return None


def find_nearest_implementation(test_file, commits):
    """
    Function to take a test_file tuple and list of commits and find the nearest commit taking before and after into account
    @param test_file: A Tuple holding the tests file name and the index in 'Commits' it can be found
    @param commits: An Array containing CustomCommit objects with one CustomCommit object per commit
    @return: Integer index where the tests nearest implementation file is (only searching future commits) or None.
    """
    # Find the location of the nearest implementation files, separately, both before and after the test files position
    after = find_nearest_after(test_file, commits)
    before = find_nearest_before(test_file, commits)

    if after == before:
        # The implementation file was committed in the same commit as the test file, OR was not found (None)
        # Therefore either 'after' or 'before' can be returned as they are the same
        return after

    # If either 'after' or 'before' is None, then the other option can be returned
    # We know at this point that they are not both none
    if after is None:
        return before
    if before is None:
        return after

    # We know that at this point, 'after' and 'before' are both numbers
    # We therefore calculate their distances from the test file
    distance_after = after - test_file[0]
    distance_before = test_file[0] - before

    if distance_after < distance_before:
        # The commit at index 'after' is closer than the commit at index 'before'
        # Return the close commit 'after'
        return after

    if distance_before < distance_after:
        # The commit at index 'before' is closer than the commit at index 'after'
        # Return the close commit 'before'
        return before


def plot_bar_graph(test_before, test_during, test_after, repo):
    """
    Function to plot a bar chart showing the order of commits for test files
    @param test_before: An Integer representing the number of tests that were committed BEFORE their corresponding implementation
    @param test_during: An Integer representing the number of tests that were committed TOGETHER with their corresponding implementation
    @param test_after: An Integer representing the number of tests that were committed AFTER their corresponding implementation
    @param repo: A String representing the repository which we will search and retrieve commits from
    """
    # Specify the bars names
    categories = ['Test Before Impl.', 'Same Time', 'Impl. Before Test']
    # Match the values for each bar
    values = [test_before, test_during, test_after]
    # Give each bar a different color
    plt.bar(categories, values, color=["#1984c5", "#22a7f0", "#63bff0"])
    # Assign the plot a title, x, and y label
    plt.title('Test and Implementation commit order. Repo: ' + repo)
    plt.xlabel('Test/Implementation Commit Order')
    plt.ylabel('Number of Test/Implementation Pairs')
    # Basic Formatting
    plt.xticks(rotation=45)
    plt.tight_layout()
    # Save the plot
    plt.savefig("./../plots/" + repo + "_plot.jpg")
    plt.show()

def main():
    # Use repository_utils to get an array from the list of allowed repositories
    repositories = repository_utils.read_repository_names("java")[1:2]

    # For each repo on the list of allowed repositories
    for repo in repositories:
        commits, test_files = gather_commits_and_tests(repo)

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
            nearest_implementation = find_nearest_implementation(test_file, commits)
            if nearest_implementation is not None:
                if test_file[0] < nearest_implementation:
                    # Test was committed before the implementation
                    array_before.append(test_file)
                    test_before += 1
                if test_file[0] > nearest_implementation:
                    # Test was committed after the implementation
                    array_after.append(test_file)
                    test_after += 1
                if test_file[0] == nearest_implementation:
                    # Test was committed in the same commit as the implementation
                    array_during.append(test_file)
                    test_during += 1

        # Output our results in the console
        print("\n")
        print("Test before Implementation: " + str(test_before))
        print("Test after Implementation: " + str(test_after))
        print("Test during Implementation: " + str(test_during))

        # Plot the bar graph using the function
        plot_bar_graph(test_before, test_during, test_after, repo.split("/")[-1].split(".")[0])

        for test_file in array_during:
            # get the author of the commit
            author = commits[test_file[0]].author.name


        '''
        PLAN

        store test files and the results in separate arrays

        at the end of the search - analyse authors work ect...

        '''



main()


