import csv
import re
from pydriller import Repository

# Define the repository URL
url = "https://github.com/apache/zookeeper.git"

# Define the output file
output_folder = 'results'
output_file = f'{output_folder}/zookeeper_tdd_analysis.csv'

# Ensure the results folder exists
import os
os.makedirs(output_folder, exist_ok=True)

# Function to infer corresponding implementation file from test file name
def map_test_to_code(test_file_name):
    """
    Maps a test file name to its probable implementation file name based on naming conventions.
    """
    base_name = re.sub(r'(test_|_test|Test)', '', test_file_name, flags=re.IGNORECASE)
    base_name = os.path.splitext(base_name)[0]  # Remove file extension
    return base_name

# Classify commits based on file relationships
def classify_commit(commit, test_files, code_files, file_history):
    """
    Classifies a commit as TDD, Mixed, or Not TDD based on the sequence of test and implementation files.
    """
    commit_type = "Not TDD"

    for test_file in test_files:
        test_file_name = test_file.filename
        implementation_name = map_test_to_code(test_file_name)

        # Check if the implementation file exists in the same commit
        for code_file in code_files:
            if implementation_name in code_file.filename:
                commit_type = "Mixed"
                break
        else:
            # Check if the implementation file was added earlier
            if implementation_name in file_history and file_history[implementation_name] <= commit.committer_date:
                commit_type = "TDD"

        # Update file history with the test file
        file_history[test_file.filename] = commit.committer_date

    return commit_type

# Main script
try:
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Commit Hash', 'Commit Message', 'Commit Date', 'Author', 'Commit Type'])

        file_history = {}
        total_commits = 0
        tdd_commits = 0
        mixed_commits = 0

        # Analyze commits using PyDriller
        for commit in Repository(url).traverse_commits():
            total_commits += 1

            # Identify test and code files in the commit
            test_files = [file for file in commit.modified_files if "test" in file.filename.lower()]
            code_files = [file for file in commit.modified_files if "test" not in file.filename.lower()]
            if not test_files or not code_files:
                continue

            # Classify the commit
            commit_type = classify_commit(commit, test_files, code_files, file_history)

            # Count classifications
            if commit_type == "TDD":
                tdd_commits += 1
            elif commit_type == "Mixed":
                mixed_commits += 1

            # Write commit data to CSV
            writer.writerow([
                commit.hash,
                commit.msg.strip(),
                commit.committer_date.strftime("%Y-%m-%d %H:%M:%S"),
                commit.author.name,
                commit_type
            ])

            # Log progress
            print(f"Processed commit {commit.hash[:7]}: {commit_type}")

        # Summary
        print("\nAnalysis Summary:")
        print(f"Total commits analyzed: {total_commits}")
        print(f"Commits following TDD: {tdd_commits}")
        print(f"Percentage of TDD commits: {tdd_commits / total_commits * 100:.2f}%")
        print(f"Percentage of Mixed commits: {mixed_commits / total_commits * 100:.2f}%")

except Exception as e:
    print(f"An error occurred: {e}")
