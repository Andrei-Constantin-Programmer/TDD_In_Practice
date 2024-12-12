
# import csv
# from pydriller import Repository
# import re

# url = "https://github.com/apache/zookeeper.git"

# # Function to determine the corresponding implementation file from a test file name

# def map_test_to_code(test_file_name):
#     # Remove common test naming patterns to get the likely implementation file name
#     patterns = ['test_', '_test', 'Test']
#     for pattern in patterns:
#         test_file_name = re.sub(pattern, '', test_file_name, flags=re.IGNORECASE)
#     return test_file_name

# output_file = 'neutral_mapped_tdd_analysis.csv'
# try:
#     with open(output_file, mode='w', newline='', encoding='utf-8') as file:
#         writer = csv.writer(file)
#         writer.writerow(['Commit Hash', 'Commit Message', 'Commit Date', 'Author', 'Test File', 'Implementation File', 'Type'])

#         prev_test_commits = {}

#         for commit in Repository(url).traverse_commits():

#             test_files = [file.filename for file in commit.modified_files if "test" in file.filename.lower()]
#             code_files = [file.filename for file in commit.modified_files if "test" not in file.filename.lower()]

#             author = commit.author.name

#             # Process each test file and map to likely implementation files
#             for test_file in test_files:
#                 implementation_file = map_test_to_code(test_file)
                
#                 if test_file and implementation_file:
#                     if implementation_file in code_files:
#                         commit_type = "Mixed"  # Neutral for now
#                     elif implementation_file in prev_test_commits.get(author, {}):
#                         commit_type = "TDD"  # Test file preceded implementation
#                     else:
#                         commit_type = "Not TDD"
#                 else:
#                     commit_type = "Mixed"

#                 # Update the last test only commit for this implementation file and author
#                 if test_file and commit_type == "TDD":
#                     if author not in prev_test_commits:
#                         prev_test_commits[author] = {}
#                     prev_test_commits[author][implementation_file] = commit

#                 writer.writerow([
#                     commit.hash,
#                     commit.msg.strip(),
#                     commit.author_date.strftime("%Y-%m-%d %H:%M:%S"),
#                     author,
#                     test_file,
#                     implementation_file,
#                     commit_type
#                 ])

#             # Print progress
#             print(f"Processed commit {commit.hash[:7]} by {author}: {commit.msg.strip()[:50]}")

#     print(f"Neutral TDD analysis completed. Results saved in '{output_file}'.")

# except Exception as e:
#     print(f"An error occurred: {e}")

import os
import repository_utils
import re
from collections import defaultdict

# map test files to implementation files
def map_test_to_code(test_file_name):
    """
    Attempts to map a test file to its corresponding implementation file based on naming conventions.
    """
    base_name = re.sub(r'(test_|_test|Test)', '', test_file_name, flags=re.IGNORECASE)
    base_name = os.path.splitext(base_name)[0]  # Remove file extension
    return base_name

# Function to classify commits
def classify_commit(commit, test_files, code_files, file_history):
    """
    Classifies a commit as TDD, Mixed, or Not TDD based on file introduction times.
    """
    commit_type = "Not TDD"
    has_test_and_code = False

    for test_file in test_files:
        implementation_name = map_test_to_code(test_file)

        # Check for implementation in the same commit
        for code_file in code_files:
            if implementation_name in code_file:
                has_test_and_code = True
                commit_type = "Mixed"
                break
        else:
            # Check file history for prior introduction
            if implementation_name in file_history:
                prior_commit_date = file_history[implementation_name]
                if prior_commit_date <= commit.committer_date:
                    commit_type = "TDD"

        file_history[test_file] = commit.committer_date

    if has_test_and_code:
        commit_type = "Mixed"

    return commit_type

csv_header = ['Commit Hash', 'Commit Message', 'Commit Date', 'Author', 'Commit Type']
rows = []

repositories = repository_utils.read_repository_names("java")[:1]

file_history = {}  # Tracks introduction times for files
unmatched_test_files = defaultdict(list)  # Tracks unmapped test files for debugging
total_commits = 0
tdd_commits = 0
mixed_commits = 0

for repo in repositories:
    output_file = f'{repo.split('/')[-1].replace('.git', '')}_tdd_analysis.csv'
    for commit in repository_utils.read_commits(repo):
        total_commits += 1

        # Identifying test and implementation files
        test_files = [file.filename for file in commit.modified_files if "test" in file.filename.lower()]
        code_files = [file.filename for file in commit.modified_files if "test" not in file.filename.lower()]

        commit_type = classify_commit(commit, test_files, code_files, file_history)

        # Track unmapped test files for debugging
        if commit_type == "Not TDD":
            for test_file in test_files:
                implementation_name = map_test_to_code(test_file)
                if implementation_name not in file_history:
                    unmatched_test_files[implementation_name].append(commit.hash)

        if commit_type == "TDD":
            tdd_commits += 1
        elif commit_type == "Mixed":
            mixed_commits += 1

        # Append row to rows list
        rows.append([
            commit.hash,
            commit.msg.strip(),
            commit.committer_date.strftime("%Y-%m-%d %H:%M:%S"),
            commit.author.name,
            commit_type,
        ])

        # Print progress
        print(f"Processed commit {commit.hash[:7]}: {commit_type}")

    print("\nAnalysis Summary:")
    print(f"Total commits analyzed: {total_commits}")
    print(f"Commits following TDD: {tdd_commits}")
    print(f"Percentage of TDD commits: {tdd_commits / total_commits * 100:.2f}%")
    print(f"Percentage of Mixed commits: {mixed_commits / total_commits * 100:.2f}%")

    print(f"Success of matched test to code files:  {len(unmatched_test_files) / total_commits * 100:.2f}%")

    repository_utils.write_csv([csv_header] + rows, output_file)
    print(f"TDD analysis completed. Results saved in '{output_file}'.")
