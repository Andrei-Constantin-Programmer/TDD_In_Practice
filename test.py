import csv
from pydriller import Repository

# Define the repository URL you want to analyze
repo_url = 'https://github.com/Andrei-Constantin-Programmer/TDD_In_Practice.git'

# Create and open a CSV file for writing
with open('commits_data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # Write the header row in the CSV file
    writer.writerow(['Commit Hash', 'Commit Message', 'Author', 'Modified File', 'Change Type'])

    # Initialize the Repository object with the desired repository URL
    for commit in Repository(repo_url).traverse_commits():
        # Extract commit information
        commit_hash = commit.hash
        commit_msg = commit.msg
        commit_author = commit.author.name

        # List of test files and production files in the commit
        test_files = []
        prod_files = []

        # Loop through modified files in each commit
        for file in commit.modified_files:
            file_name = file.filename
            change_type = file.change_type.name
            lines_added = getattr(file, 'lines_added', 0)
            lines_removed = getattr(file, 'lines_removed', 0)

            # Classify files as test or production files
            if 'test' in file_name.lower() or 'Test' in file_name:
                test_files.append((file_name, change_type))
            else:
                prod_files.append((file_name, change_type))

            # Write the commit data for each modified file
            writer.writerow([commit_hash, commit_msg, commit_author, file_name, change_type])

        # Check if the commit follows TDD or TFD
        tdd_tfd_label = ""
        if test_files and prod_files:
            # If a test file appears before a production file in the commit, it's likely TDD
            test_first_commit = False
            for test_file, _ in test_files:
                for prod_file, _ in prod_files:
                    if test_file < prod_file:  # If the test file comes before the production file
                        test_first_commit = True
                        break
            tdd_tfd_label = "TDD" if test_first_commit else "TFD"

        # Add the TDD/TFD label to the CSV
        writer.writerow([commit_hash, commit_msg, commit_author, '', ''])

print("Data export completed! The data is saved in 'commits_data.csv'.")

