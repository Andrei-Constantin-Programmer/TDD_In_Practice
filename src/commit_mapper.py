from pydriller import Repository
import repository_utils
import matplotlib.pyplot as plt
from collections import defaultdict
import datetime

# Function to determine if a corresponding implementation file exists in the same commit
def find_corresponding_implementation(test_file_name, modified_files):
    # Remove typical test suffixes and try to match the implementation file
    potential_impl_file = test_file_name.replace("Tests", "").replace("Test", "")
    for file in modified_files:
        if potential_impl_file in file.filename and file.filename != test_file_name:
            return file.filename
    return None

def main():
    repositories = repository_utils.read_repository_names("java")[1:2]

    # Dictionaries to store file commit history: file_name -> list of commit times
    file_commit_history = defaultdict(list)

    # We'll first build a history of all files, then do analysis after
    for repo in repositories:
        print("Running on " + repo.split('/')[-1].strip('.git') + '\n')
        for commit in repository_utils.read_commits(repo):
            commit_time = commit.author_date
            # Record each file and when it appeared/modified
            for file in commit.modified_files:
                # We track every commit time this file shows up
                # (If we want only first appearance, we can handle that later)
                file_commit_history[file.filename].append(commit_time)

    # After we've collected the full history, we re-run the logic to find matches.
    # Alternatively, we could do it in the same loop, but let's keep it separate for clarity.

    no_test_files = 0
    found_files = 0
    lone_files = 0
    matched = []
    unmatched = []

    # We need to re-check the commits because we rely on the matching logic
    # done at the time of the commit. If we only rely on earliest appearances,
    # we might lose the association that was made in a specific commit.
    for repo in repositories:
        for commit in repository_utils.read_commits(repo):
            for file in commit.modified_files:
                if "Test" in file.filename:
                    no_test_files += 1
                    corresponding_file = find_corresponding_implementation(file.filename, commit.modified_files)
                    if corresponding_file:
                        found_files += 1
                        matched.append((file.filename, corresponding_file))
                    else:
                        unmatched.append(file.filename)
                        lone_files += 1

    print("Files with NO corresponding implementation files:")
    for filename in unmatched:
        print(filename)

    print("\nTotal number of test files: " + str(no_test_files))
    print("Test files with corresponding implementation files: " + str(found_files))
    print("Test files with NO corresponding implementation files: " + str(lone_files))
    print("Success Rate: " + str(round(found_files / no_test_files * 100, 2)) + "%")

    # Now we analyze the timeline for the matched files.
    # We will consider the earliest known commit time for each file.
    def earliest_commit(file_name):
        if file_name in file_commit_history:
            return min(file_commit_history[file_name])
        return None

    before_count = 0
    same_time_count = 0
    after_count = 0

    # We'll store details to print later
    timeline_details = []

    for test_file, impl_file in matched:
        test_earliest = earliest_commit(test_file)
        impl_earliest = earliest_commit(impl_file)

        if test_earliest and impl_earliest:
            if test_earliest < impl_earliest:
                # Test appeared before implementation
                before_count += 1
                timeline_details.append((test_file, impl_file, "TEST BEFORE IMPL", test_earliest, impl_earliest))
            elif test_earliest > impl_earliest:
                # Implementation appeared before test
                after_count += 1
                timeline_details.append((test_file, impl_file, "IMPL BEFORE TEST", test_earliest, impl_earliest))
            else:
                # Same commit time
                same_time_count += 1
                timeline_details.append((test_file, impl_file, "SAME TIME", test_earliest, impl_earliest))

    print("\nTimeline Analysis:")
    print("Test introduced before Implementation:", before_count)
    print("Implementation introduced before Test:", after_count)
    print("Introduced at the same time:", same_time_count)

    # Optional: print details
    # for detail in timeline_details:
    #     print(detail)

    # Visualization
    # We'll create a simple bar chart showing the counts of each category
    categories = ['Test Before Impl', 'Same Time', 'Impl Before Test']
    values = [before_count, same_time_count, after_count]

    plt.bar(categories, values, color=['blue', 'green', 'red'])
    plt.title('Relative Introduction Times of Test and Implementation Files')
    plt.xlabel('Introduction Timing')
    plt.ylabel('Number of Matched Pairs')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

main()
