import os
import matplotlib.pyplot as plt
import numpy as np
from src.infrastructure import file_utils

def _save_plot(plot: plt, name: str):
    file_path = os.path.join(file_utils.CHARTS_PATH, f"{name}.jpg")
    plot.savefig(file_path)

def _create_size_impact_plot():
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
        # we don't count test_during as we want TDD percentage, not before, during and after percentage
        total_test_count = int(repo['Test Before']) + int(repo['Test After'])
        total_test_count = 1 if total_test_count == 0 else total_test_count

        # Append the percentage of TDD for the repo to Y
        y.append((int(repo['Test Before'])/total_test_count)*100)

    # Convert arrays to numpy arrays
    x = np.array(x)
    y = np.array(y)

    # Clear any existing plot
    plt.clf()

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

    # Save the plot
    _save_plot(plt, "Size Impact")

def _create_box_plot():
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

    # Clear any existing plot
    plt.clf()

    # Plot the box plots
    boxplt = plt.boxplot([before, after, during], patch_artist=True, tick_labels=["Before", "After", "During"], flierprops= dict(markerfacecolor='coral'))

    # Give each bar a color
    colors = ['palegreen', 'lightblue', 'lightskyblue']
    for patch, color in zip(boxplt['boxes'], colors):
        patch.set_facecolor(color)

    # Set title and axes labels
    plt.ylabel("Percentage of tests")
    plt.title("Percentage of tests created before, after and during implementation")

    # Save the plot
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

    # Clear any existing plot
    plt.clf()

    # Plot the bar chart
    colors = ['palegreen', 'lightblue', 'lightskyblue']
    plt.bar(["Before", "After", "During"], [before_avg, after_avg, during_avg], align='center', color=colors)
    plt.bar(["Before", "After", "During"], [before_avg, after_avg, during_avg], align='center', color=colors)

    # Set title and axes labels
    plt.ylabel("Average Commit Size (No. of files)")
    plt.title("Average commit size when tests are created \nbefore, after and during implementation")

    # Save the plot
    _save_plot(plt, "Average Commit Size")


def _create_pie_plot_tdd_levels():
    # Read data from the author_data csv
    author_data = file_utils.read_csv("author_data")

    # Initialize Counters
    #10 25 50 70 90 100
    counters = [0,0,0,0,0,0]


    for author in author_data:
        # Calculate the percentage of TDD of the author
        # we don't count test_during as we want TDD percentage, not before, during and after percentage
        TDD_percent = (float(author['Test Before']) / max(1, float(author['Test Before']) + float(author['Test After']))) * 100

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

    # Update labels to include percentage values for each slice
    labels = ['Non TDD', 'Rarely TDD', 'Occasionally TDD', 'Somewhat TDD', 'Mostly TDD', 'Consistently TDD']
    for i in range(len(labels)):
        labels[i] = labels[i] + ' - ' + str(round(percentages[i], 0)) + '%'

    # Clear any existing plot
    plt.clf()

    # Plot the pie
    colors = ['#225ea8', '#1d91c0', '#41b6c4', '#7fcdbb', '#c7e9b4', '#71cb71']
    patches, texts = plt.pie(percentages, colors=colors)

    # Plot the legend
    plt.legend(patches, labels, loc="upper left")

    # Set the title and specify axis setting
    plt.axis('equal')
    plt.title("Pie chart showing the percentage of authors using levels of TDD")
    plt.rcParams["figure.figsize"] = [7.5, 4.25]
    plt.rcParams["figure.autolayout"] = True

    # Save the plot
    _save_plot(plt, "TDD Categories")


def _create_pie_plot_tdd_overall():
    # Read data from the author_data csv
    repo_data = file_utils.read_csv("repo_data")

    # Initialize Counters
    total = 0
    data = [0, 0, 0]

    for repo in repo_data:
        data[0] += int(repo['Test Before'])
        data[1] += int(repo['Test After'])
        data[2] += int(repo['Test During'])
        total += int(repo['Test Before']) + int(repo['Test After']) + int(repo['Test During'])

    # Convert the data into percentages using a lambda function and map
    percentages = list(map(lambda x: x / max(1, total) * 100, data))


    # Update labels to include percentage values for each slice
    labels = ['TDD', 'Not TDD', 'Unclear']
    for i in range(len(labels)):
        labels[i] = labels[i] + ' - ' + str(round(percentages[i], 0)) + '%'

    # Clear any existing plot
    plt.clf()

    # Plot the pie
    colors = ['palegreen', 'lightblue', 'lightskyblue']
    patches, texts, x = plt.pie(percentages, colors=colors, autopct='%1.1f%%')

    # Plot the legend
    plt.legend(patches, labels, loc="upper left")

    # Set the title and specify axis setting
    plt.axis('equal')
    plt.title("Overall TDD Percentage (Raw Data)")
    plt.rcParams["figure.figsize"] = [7.5, 4.25]
    plt.rcParams["figure.autolayout"] = True

    # Save the plot
    _save_plot(plt, "Overall TDD Usage Raw")

def create_plots():
    _create_box_plot()
    _create_size_impact_plot()
    _create_avg_commit_size_plot()
    _create_pie_plot_tdd_levels()
    _create_pie_plot_tdd_overall()

create_plots()

'''
todo - 
write the adjustments/estimates code in python

todo - 
plot like the TDD cagetories pie, but for repo instead of author - modify _create_pie_plot_tdd_levels
bar chart for tdd percentace per langange - ignoring during
average code on line 97 is completely wrong because of the 0
overall tdd percentage - pie of before and after, excluding during

'''