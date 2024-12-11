# from pydriller import Repository
# import csv




# url = "https://github.com/Andrei-Constantin-Programmer/TDD_In_Practice.git"
# with open('commit_data.csv', mode='w', newline='', encoding='utf-8') as file:

#     writer = csv.writer(file)
#     writer.writerow(['Commit Hash ', ' Commit Message ',' Commit Date '])
#     writer.writerow("")

#     for commit in Repository(url).traverse_commits():
#         commit_data = {
#             "Commit Hash": commit.hash,
#             "Commit Message": commit.msg,
#             "Commit Date": commit.author_date
#     }
        
#         writer.writerow([commit_data["Commit Hash"], commit_data["Commit Message"], commit_data["Commit Date"]])


# import csv
# from pydriller import Repository

# url = "https://github.com/Andrei-Constantin-Programmer/TDD_In_Practice.git"

# # Define keywords for TDD-related commit messages
# tdd_keywords = ['test', 'refactor', 'fix', 'feature', 'add']

# with open('tdd_commits.csv', mode='w', newline='', encoding='utf-8') as file:
#     writer = csv.writer(file)
#     writer.writerow(['Commit Hash', 'Commit Message', 'Commit Date', 'Type', 'TDD Approach'])

#     prev_test_commit = None  # Track the last test related commit
#     for commit in Repository(url).traverse_commits():
        
#         test_files = [file for file in commit.modified_files if "test" in file.filename.lower()]
#         code_files = [file for file in commit.modified_files if "test" not in file.filename.lower()]
        
#         # Determine the commit type
#         if test_files and not code_files:
#             commit_type = "Test-Only"
#         elif test_files and code_files:
#             commit_type = "Mixed"
#         else:
#             commit_type = "Code-Only"

#         # Check if the commit message mentions testing
#         is_tdd_message = any(keyword in commit.msg.lower() for keyword in tdd_keywords)

#         # Determine if the commit follows a TDD approach
#         is_tdd_approach = False

#         if commit_type == "Code-Only" and prev_test_commit:
#             is_tdd_approach = True

#         elif commit_type == "Mixed" and is_tdd_message:
#             # Mixed commits with test related messages might indicate TDD
#             is_tdd_approach = True

#         # Update the previous test commit
#         if commit_type == "Test-Only":
#             prev_test_commit = commit

#         # Writing the analysis to the CSV file
#         writer.writerow([
#             commit.hash, 
#             commit.msg.strip(), 
#             commit.author_date, 
#             commit_type, 
#             "Yes" if is_tdd_approach else "No"
#         ])

# print("TDD analysis completed. Results saved in 'tdd_commits.csv'.")

import repository_utils
import re

# Function to determine the corresponding implementation file from a test file name

def map_test_to_code(test_file_name):
    # Remove common test naming patterns to get the likely implementation file name
    patterns = ['test_', '_test', 'Test']
    for pattern in patterns:
        test_file_name = re.sub(pattern, '', test_file_name, flags=re.IGNORECASE)
    return test_file_name

output_file = 'neutral_mapped_tdd_analysis.csv'
csv_header = ['Commit Hash', 'Commit Message', 'Commit Date', 'Author', 'Test File', 'Implementation File', 'Type']
rows = []

repositories = repository_utils.read_repository_names("java")[:1]
prev_test_commits = {}

for repo in repositories:
    for commit in repository_utils.read_commits(repo):
        test_files = [file.filename for file in commit.modified_files if "test" in file.filename.lower()]
        code_files = [file.filename for file in commit.modified_files if "test" not in file.filename.lower()]

        author = commit.author.name

        # Process each test file and map to likely implementation files
        for test_file in test_files:
            implementation_file = map_test_to_code(test_file)
            
            if test_file and implementation_file:
                if implementation_file in code_files:
                    commit_type = "Mixed"  # Neutral for now
                elif implementation_file in prev_test_commits.get(author, {}):
                    commit_type = "TDD"  # Test file preceded implementation
                else:
                    commit_type = "Not TDD"
            else:
                commit_type = "Mixed"

            # Update the last test-only commit for this implementation file and author
            if test_file and commit_type == "TDD":
                if author not in prev_test_commits:
                    prev_test_commits[author] = {}
                prev_test_commits[author][implementation_file] = commit

            # Append row to rows list
            rows.append([
                commit.hash,
                commit.msg.strip(),
                commit.author_date.strftime("%Y-%m-%d %H:%M:%S"),
                author,
                test_file,
                implementation_file,
                commit_type
            ])

        # Print progress
        print(f"Processed commit {commit.hash[:7]} by {author}: {commit.msg.strip()[:50]}")

repository_utils.write_csv([csv_header] + rows, output_file)
print(f"Neutral TDD analysis completed. Results saved in 'results/{output_file}.csv'.")
