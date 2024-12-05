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


import csv
from pydriller import Repository

url = "https://github.com/Andrei-Constantin-Programmer/TDD_In_Practice.git"

# Define keywords for TDD-related commit messages
tdd_keywords = ['test', 'refactor', 'fix', 'feature', 'add']

with open('tdd_commits.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Commit Hash', 'Commit Message', 'Commit Date', 'Type', 'TDD Approach'])

    prev_test_commit = None  # Track the last test related commit
    for commit in Repository(url).traverse_commits():
        
        test_files = [file for file in commit.modified_files if "test" in file.filename.lower()]
        code_files = [file for file in commit.modified_files if "test" not in file.filename.lower()]
        
        # Determine the commit type
        if test_files and not code_files:
            commit_type = "Test-Only"
        elif test_files and code_files:
            commit_type = "Mixed"
        else:
            commit_type = "Code-Only"

        # Check if the commit message mentions testing
        is_tdd_message = any(keyword in commit.msg.lower() for keyword in tdd_keywords)

        # Determine if the commit follows a TDD approach
        is_tdd_approach = False

        if commit_type == "Code-Only" and prev_test_commit:
            is_tdd_approach = True

        elif commit_type == "Mixed" and is_tdd_message:
            # Mixed commits with test related messages might indicate TDD
            is_tdd_approach = True

        # Update the previous test commit
        if commit_type == "Test-Only":
            prev_test_commit = commit

        # Writing the analysis to the CSV file
        writer.writerow([
            commit.hash, 
            commit.msg.strip(), 
            commit.author_date, 
            commit_type, 
            "Yes" if is_tdd_approach else "No"
        ])

print("TDD analysis completed. Results saved in 'tdd_commits.csv'.")
