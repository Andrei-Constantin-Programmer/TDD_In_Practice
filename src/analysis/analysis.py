import os
import matplotlib.pyplot as plt
import numpy as np
from src.infrastructure import file_utils, repository_utils

def _save_plot(plot: plt, name: str):
    file_path = os.path.join(file_utils.CHARTS_PATH, f"{name}.jpg")
    plot.savefig(file_path, dpi=300)

def _create_size_impact_plot():
    # 3. How does the size of a commit impact the results?

    # Read data from the repo_data csv
    repo_data = file_utils.read_csv("repo_data")

    # Initialize arrays to store plot points
    x = []
    y = []

    # Iterate through each repo and create a point in the two arrays
    for repo in repo_data:
        # Append the commit count of the repo to X
        x.append(int(repo['Commit Count']))

        # Get the total number of tests for the repo
        total_test_count = int(repo['Test Before']) + int(repo['Test During']) + int(repo['Test After'])
        total_test_count = 1 if total_test_count == 0 else total_test_count

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
    plt.xlabel("Repo Size (No. of files)")
    plt.xlabel("Repo Size (No. of files)")
    plt.ylabel("Percentage of TDD")
    plt.title("Repo size and TDD percentage")
    _save_plot(plt, "Size Impact")

def _create_box_plot():
    # 2. How often is a test class (file) created (a) before, (b) after, or (c) in the same commit as a tested class (file)?

    # Read data from the repo_data csv
    repo_data = file_utils.read_csv("repo_data")

    # Initialize arrays to store percentages for each repo
    before = []
    after = []
    during = []

    # Iterate through each repo and append the before, during and after percentages to each array
    for repo in repo_data:
        # Get the total number of tests for the repo
        total_test_count = int(repo['Test Before']) + int(repo['Test During']) + int(repo['Test After'])
        total_test_count = 1 if total_test_count == 0 else total_test_count

        # Append the percentage data to each array
        before.append((int(repo['Test Before']) / total_test_count) * 100)
        after.append((int(repo['Test After']) / total_test_count) * 100)
        during.append((int(repo['Test During']) / total_test_count) * 100)

    # Plot the box plots
    boxplt = plt.boxplot([before, after, during], patch_artist=True, tick_labels=["Before", "After", "During"], flierprops= dict(markerfacecolor='coral'))
    boxplt = plt.boxplot([before, after, during], patch_artist=True, tick_labels=["Before", "After", "During"], flierprops= dict(markerfacecolor='coral'))

    colors = ['palegreen', 'lightblue', 'lightskyblue']
    for patch, color in zip(boxplt['boxes'], colors):
        patch.set_facecolor(color)

    # Set title and axes labels
    plt.ylabel("Percentage")
    plt.title("How often a test is created before, after and during implementation")
    _save_plot(plt, "TDD Usage Statistics")


def _create_avg_commit_size_plot():
    # Read data from the repo_data csv
    repo_data = file_utils.read_csv("repo_data")

    # Initialize variables to store averages for each repo
    before_avg  = 0
    after_avg = 0
    during_avg = 0

    # Iterate through each repo and update the before, during and after averages
    for repo in repo_data:
        before_avg = (before_avg + float(repo['Avg Before Commit Size'])) / 2
        after_avg = (after_avg + float(repo['Avg After Commit Size'])) / 2
        during_avg = (during_avg + float(repo['Avg During Commit Size'])) / 2

    # Plot the bar chart
    colors = ['palegreen', 'lightblue', 'lightskyblue']
    plt.bar(["Before", "After", "During"], [before_avg, after_avg, during_avg], align='center', color=colors)
    plt.bar(["Before", "After", "During"], [before_avg, after_avg, during_avg], align='center', color=colors)

    # Set title and axes labels
    plt.ylabel("Average Commit Size (No. of files)")
    plt.title("Average commit size when tests are created \nbefore, after and during implementation")
    _save_plot(plt, "Average Commit Size")


def _create_pie_plot():
    # Read data from the author_data csv
    author_data = file_utils.read_csv("author_data")

    # Initialize Counters
    #10 25 50 70 90 100
    counters = [0,0,0,0,0,0]


    for author in author_data:
        # Calculate the percentage of TDD of the author
        TDD_percent = (float(author['Test Before']) / max(1, float(author['Test Before']) + float(author['Test During']) + float(author['Test After']))) * 100

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
    percentages = list(map(lambda x: x/max(1, len(author_data))*100, counters))

    labels = ['Non TDD', 'Rarely TDD', 'Occasionally TDD', 'Somewhat TDD', 'Mostly TDD', 'Consistently TDD']
    for i in range(len(labels)):
        labels[i] = labels[i] + ' - ' + str(round(percentages[i], 0)) + '%'

    # Set up and plot the pie chart, colors, legend and title
    colours = ['#225ea8', '#1d91c0', '#41b6c4', '#7fcdbb', '#c7e9b4', '#71cb71']
    plt.rcParams["figure.figsize"] = [7.5, 4.25]
    plt.rcParams["figure.autolayout"] = True
    patches, texts = plt.pie(percentages, colors=colours)
    plt.legend(patches, labels, loc="upper left")
    plt.axis('equal')
    plt.title("Pie chart showing the percentage of authors using levels of TDD")
    _save_plot(plt, "TDD Categories")


def create_plots():
    _create_size_impact_plot()
    _create_box_plot()
    _create_avg_commit_size_plot()
    _create_pie_plot()
