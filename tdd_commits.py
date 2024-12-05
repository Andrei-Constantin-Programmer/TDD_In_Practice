
import csv

def analyze_tdd_commits(input_file, output_file):
    """
    Analysing TDD-related commit sequences and save valid TDD commit sequences to the output file.
    """
    tdd_sequences = []
    ongoing_tdd_sequence = []  

    with open(input_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            commit_type = row['Type']
            commit_hash = row['Commit Hash']
            commit_message = row['Commit Message']
            tdd_approach = row['TDD Approach'].lower() == 'yes'

            if commit_type == "Test-Only":
                # Start a new TDD sequence with the Test only commit
                ongoing_tdd_sequence = [row]

            elif commit_type == "Code-Only" and ongoing_tdd_sequence:
                # A Code only commit after a Test only commit indicates implementation
                ongoing_tdd_sequence.append(row)
                tdd_sequences.append(ongoing_tdd_sequence)  
                ongoing_tdd_sequence = []  

            elif commit_type == "Mixed" and tdd_approach:
                if ongoing_tdd_sequence:
                    ongoing_tdd_sequence.append(row)
                    tdd_sequences.append(ongoing_tdd_sequence)  
                else:
                    tdd_sequences.append([row])  # Handle isolated valid TDD Mixed commits
                ongoing_tdd_sequence = []

    # Writing the valid TDD sequences to a new csv file
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Sequence Step', 'Commit Hash', 'Commit Message', 'Commit Date', 'Type', 'TDD Approach'])

        for sequence in tdd_sequences:
            for step, commit in enumerate(sequence, start=1):
                writer.writerow([
                    f"Step {step}",
                    commit['Commit Hash'],
                    commit['Commit Message'],
                    commit['Commit Date'],
                    commit['Type'],
                    commit['TDD Approach']
                ])

    print(f"Valid TDD sequences have been saved to '{output_file}'.")

analyze_tdd_commits('tdd_commits.csv', 'valid_tdd_sequences.csv')
