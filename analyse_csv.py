import csv

input_file = 'mapped_tdd_analysis.csv'

try:
    tdd_count = 0
    total_count = 0

    with open(input_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            total_count += 1
            if row['Type'] == 'TDD':
                tdd_count += 1

    # Calculate the percentage of TDD
    tdd_percentage = (tdd_count / total_count) * 100 if total_count > 0 else 0

    print(f"Total commits analyzed: {total_count}")
    print(f"Commits following TDD: {tdd_count}")
    print(f"Percentage of TDD commits: {tdd_percentage:.2f}%")

except FileNotFoundError:
    print(f"File '{input_file}' not found. Please ensure it exists and try again.")
except Exception as e:
    print(f"An error occurred: {e}")
