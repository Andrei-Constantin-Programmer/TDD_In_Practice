from pydriller import Repository
from tqdm import tqdm  # For the progress bar

# Function to determine if a corresponding implementation file exists
def find_corresponding_implementation(test_file_name, modified_files):
    # Remove "test" from the name and try to match the implementation file
    potential_impl_file = test_file_name.replace("Test", "").replace("test", "")
    for file in modified_files:
        if potential_impl_file in file.filename and file.filename != test_file_name:
            return file.filename
    return None

def main():
    found_files = 0
    lone_files = 0

    # Analyze the repository
    commits = list(Repository('https://github.com/apache/harmony-classlib').traverse_commits())
    total_commits = len(commits)

    with tqdm(total=total_commits, desc="Processing Commits") as pbar:  # Initialize progress bar
        for commit in commits:
            for file in commit.modified_files:
                if ".java" in file.filename:
                    if "test" in file.filename.lower():  # Identify test files
                        corresponding_file = find_corresponding_implementation(file.filename, commit.modified_files)
                        if corresponding_file:
                            found_files += 1
                        else:
                            lone_files += 1
            pbar.update(1)  # Update progress bar after processing each commit

    print("\nSummary:")
    print(f"Test files with corresponding implementation files: {found_files}")
    print(f"Test files with NO corresponding implementation files: {lone_files}")

if __name__ == "__main__":
    main()
