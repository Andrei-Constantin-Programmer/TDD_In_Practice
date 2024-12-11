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

    for repo in repositories:
        found_files = 0
        lone_files = 0
        no_test_files = 0
        # Analyze the repository
        for commit in repository_utils.read_commits(repo):
            #print(commit.msg)
            for file in commit.modified_files:
                #if ".java" in file.filename:
                    if "Test" in file.filename:  # Identify test files
                        no_test_files += 1
                        corresponding_file = find_corresponding_implementation(file.filename, commit.modified_files)
                        if corresponding_file:
                            #print(f"Test File: {file.filename} --> Implementation File: {corresponding_file}")
                            found_files += 1
                        else:
                            print(f"Test File: {file.filename} --> No corresponding implementation file found.")
                            lone_files += 1

    print("Total number of test files: " + str(no_test_files))
    print("Test files with corresponding implementation files: " + str(found_files))
    print("Test files with NO corresponding implementation files: " + str(lone_files))

main()

# we need to remove test or tests
#