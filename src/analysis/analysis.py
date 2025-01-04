from src.infrastructure.file_utils import read_csv
import matplotlib.pyplot as plt
import numpy as np

def create_size_impact_plot():
    # 3. How does the size of a commit impact the results?

    # Read data from the repo_data csv
    repo_data = read_csv("repo_data")

    # Initialize arrays to store plot points
    x = []
    y = []

    # Iterate through each repo and create a point in the two arrays
    for repo in repo_data:
        # Append the commit count of the repo to X
        x.append(int(repo['Commit Count']))

        # Get the total number of tests for the repo
        total_test_count = int(repo['Test Before']) + int(repo['Test During']) + int(repo['Test After'])

        # Append the percentage of TDD for the repo to Y
        y.append((int(repo['Test Before'])/total_test_count)*100)

    # Convert arrays to numpy arrays
    x = np.array(x)
    y = np.array(y)

    # Plot the scatter points
    plt.scatter(x, y, c=y, cmap = 'winter')

    # Calculate and plot the line of best fit
    a, b = np.polyfit(x, y, 1)
    plt.plot(x, a * x + b, color="red", alpha=0.5)

    # Set title and axes labels
    plt.xlabel("Commit Count")
    plt.ylabel("Percentage of TDD")
    plt.title("Scatter plot showing how the size of commits impacts results")

    # Show the plot
    plt.show()

def create_box_plot():
    # 2. How often is a test class (file) created (a) before, (b) after, or (c) in the same commit as a tested class (file)?

    # Read data from the repo_data csv
    repo_data = read_csv("repo_data")

    # Initialize arrays to store percentages for each repo
    before = []
    during = []
    after = []

    # Iterate through each repo and append the before, during and after percentages to each array
    for repo in repo_data:
        # Get the total number of tests for the repo
        total_test_count = int(repo['Test Before']) + int(repo['Test During']) + int(repo['Test After'])

        # Append the percentage data to each array
        before.append((int(repo['Test Before']) / total_test_count) * 100)
        during.append((int(repo['Test During']) / total_test_count) * 100)
        after.append((int(repo['Test After']) / total_test_count) * 100)

    # Plot the box plots
    boxplt = plt.boxplot([before, during, after], patch_artist=True, tick_labels=["Before", "During", "After"], flierprops= dict(markerfacecolor='coral'))

    colors = ['lightskyblue', 'paleturquoise', 'palegreen']
    for patch, color in zip(boxplt['boxes'], colors):
        patch.set_facecolor(color)

    # Set title and axes labels
    plt.ylabel("Percentage")
    plt.title("Boxplot showing how often a test is created\nbefore, during and after implementation")

    # Show the plot
    plt.show()


def create_avg_commit_size_plot():
    # Read data from the repo_data csv
    repo_data = read_csv("repo_data")

    # Initialize variables to store averages for each repo
    before_avg  = 0
    during_avg = 0
    after_avg = 0

    # Iterate through each repo and update the before, during and after averages
    for repo in repo_data:
        before_avg = (before_avg + float(repo['Avg Before Commit Size'])) / 2
        during_avg = (during_avg + float(repo['Avg During Commit Size'])) / 2
        after_avg = (after_avg + float(repo['Avg After Commit Size'])) / 2

    # Plot the bar chart
    plt.bar(["Before", "During", "After"], [before_avg, during_avg, after_avg], align='center')
    # Show the plot
    plt.show()


def create_pie_plot():
    # Read data from the author_data csv
    author_data = read_csv("author_data")

    # Initialize Counters
    #10 25 50 70 90 100
    counters = [0,0,0,0,0,0]


    for author in author_data:
        # Calculate the percentage of TDD of the author
        TDD_percent = (float(author['Test Before']) / (float(author['Test Before']) + float(author['Test During']) + float(author['Test After']))) * 100

        # Update the counters array based on this result
        if TDD_percent < 10:
            counters[0] += 1
        elif TDD_percent < 25:
            counters[1] += 1
        elif TDD_percent < 50:
            counters[2] += 1
        elif TDD_percent < 70:
            counters[3] += 1
        elif TDD_percent < 90:
            counters[4] += 1
        elif TDD_percent < 100:
            counters[5] += 1

    # Convert the counters into percentages using a lambda function and map
    percentages = list(map(lambda x: x/len(author_data)*100, counters))

    labels = ['Non TDD', 'Rarely TDD', 'Occasionally TDD', 'Somewhat TDD', 'Mostly TDD', 'Consistently TDD']
    for i in range(len(labels)):
        labels[i] = labels[i] + ' - ' + str(round(percentages[i], 0)) + '%'

    # Plot the pie chart
    plt.rcParams["figure.figsize"] = [7.5, 4.25]
    plt.rcParams["figure.autolayout"] = True

    patches, texts = plt.pie(percentages)

    plt.legend(patches, labels, loc="upper left")
    plt.axis('equal')

    # Show the plot
    plt.show()

#create_size_impact_plot()
#create_box_plot()
#create_avg_commit_size_plot()
create_pie_plot()

'''

8. How does TDD adoption vary between projects?

'''


