import csv

def remove_duplicate_lines(input_file, output_file):
    unique_lines = set() 

    with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        rows = list(reader)

        for row in rows:
            unique_lines.add(tuple(row))

    with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(unique_lines)

input_csv = "/repos_to_analyse/repos.csv"
output_csv = "/repos_to_analyse/unique_repos.csv"
remove_duplicate_lines(input_csv, output_csv)

print(f"Unique lines have been written to {output_csv}")