import csv
import read_write

input_file = 'neutral_mapped_tdd_analysis.csv'

tdd_count = 0
total_count = 0
mixed_count = 0

rows = read_write.read_csv(input_file)

for row in rows:
    total_count += 1
    if row['Type'] == 'TDD':
        tdd_count += 1
    elif row['Type'] == 'Mixed':
        mixed_count += 1

# Calculate the percentage of TDD
tdd_percentage = (tdd_count / total_count) * 100 if total_count > 0 else 0
mixed_percentage = (mixed_count / total_count) * 100 if total_count > 0 else 0

print(f"Total commits analyzed: {total_count}")
print(f"Commits following TDD: {tdd_count}")
print(f"Percentage of TDD commits: {tdd_percentage:.2f}%")
print(f"Percentage of Mixed commits: {mixed_percentage:.2f}%")