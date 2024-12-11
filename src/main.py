from pydriller import Repository
import repository_utils

# Function to determine if a corresponding implementation file exists
def find_corresponding_implementation(test_file_name, modified_files):
    # Remove "test" from the name and try to match the implementation file
    potential_impl_file = test_file_name.replace("Tests", "").replace("Test", "")
    for file in modified_files:
        if potential_impl_file in file.filename and file.filename != test_file_name:
            return file.filename
    return None

def main():
    repositories = repository_utils.read_repository_names("java")[1:2]

    # Initialize Counters
    found_files = 0
    lone_files = 0
    no_test_files = 0
    matched = []
    unmatched = []

    for repo in repositories:
        print("Running on " + repo.split('/')[-1].strip('.git') + '\n')
        # Look through each commit
        for commit in repository_utils.read_commits(repo):
            # Look through each file in the commits modified files
            for file in commit.modified_files:
                # Identify test files
                if "Test" in file.filename:
                    no_test_files += 1
                    corresponding_file = find_corresponding_implementation(file.filename, commit.modified_files)
                    if corresponding_file:
                        found_files += 1
                        matched.append((file.filename, corresponding_file))
                    else:
                        unmatched.append(file.filename)
                        lone_files += 1

    print("Files with NO corresponding implementation files")
    for filename in unmatched:
        print(filename)

    print("\nTotal number of test files: " + str(no_test_files))
    print("Test files with corresponding implementation files: " + str(found_files))
    print("Test files with NO corresponding implementation files: " + str(lone_files))
    print("Success Rate: " + str(round(found_files / no_test_files * 100, 2)) + "%")

main()
