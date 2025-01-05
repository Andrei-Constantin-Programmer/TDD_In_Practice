from src.infrastructure import file_utils

def _generate_array(existing_data, new_headers):
    # Initialize an empty array for new data to go in
    new_data = []

    for row in existing_data:
        # for each existing row, create an array to represent the row from the dictionary
        new_row = []
        for header in new_headers:
            new_row.append(row[header])

        # append this row to the new_data array
        new_data.append(new_row)

    # return the new data array and prepend the headers to this array
    return [new_headers] + new_data


def make_adjustments(filename):
    existing_data = file_utils.read_csv(filename)

    for row in existing_data:
        # Calculate the tdd percentage
        try:
            tdd_percentage = int(row['Test Before']) / (int(row['Test Before']) + int(row['Test After']))
        except ZeroDivisionError:
            tdd_percentage = 0

        # Calculate the adjusted variables
        adjusted_test_before = int(row['Test Before']) + (tdd_percentage * int(row['Test During']))
        adjusted_test_after = int(row['Test After']) + ((1 - tdd_percentage) * int(row['Test During']))

        # Create a new item in the dictionary to store the new data
        row['Adjusted Test Before'] = int(adjusted_test_before)
        row['Adjusted Test After'] = int(adjusted_test_after)

    # Get the headers of the relevant file
    headers = []
    if filename == 'author_data':
        headers = ["Author", "Test Before", "Test After", "Test During"]
    elif filename == 'repo_data':
        headers = ["Repo Name", "Language", "Commit Count", "Test Before", "Test After", "Test During", "Duration (s)",
                "Avg Before Commit Size", "Avg After Commit Size", "Avg During Commit Size", "Avg Commit Size"]

    # Generate the new data as a 2D array from the dictionary
    new_data = _generate_array(existing_data, headers + ["Adjusted Test Before", "Adjusted Test After"])

    # Write this data to a new csv
    file_utils.write_csv(new_data, filename+'_adjusted')