import os
import matplotlib.pyplot as plt
import numpy as np
from src.infrastructure import file_utils
from src.analysis.adjustments import make_adjustments

def _save_plot(plot: plt, name: str):
    file_path = os.path.join(file_utils.CHARTS_PATH, f"{name}.jpg")
    plot.savefig(file_path)


def _get_category_index(tdd_percentage):
    # Return which index to increment - 10 25 50 70 90 100
    if tdd_percentage < 10:
        return 0
    elif tdd_percentage < 25:
        return 1
    elif tdd_percentage < 50:
        return 2
    elif tdd_percentage < 70:
        return 3
    elif tdd_percentage < 90:
        return 4
    elif tdd_percentage <= 100:
        return 5

def _create_size_impact_scatter():
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
    plt.ylabel("TDD Percentage (%)")
    plt.title("Repo size and TDD percentage")

    # Save the plot
    _save_plot(plt, "1 - Size Impact")

def _create_tdd_usage_box_plot():
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
    _save_plot(plt, "2 - TDD Usage Statistics")


def _create_avg_commit_size_bar_graph():
    # Read data from the repo_data csv
    repo_data = file_utils.read_csv("repo_data")

    # Initialize variables to store total for each repo
    before_total  = 0
    after_total = 0
    during_total = 0

    # Iterate through each repo and update the before, during and after totals
    for repo in repo_data:
        before_total += float(repo['Avg Before Commit Size'])
        after_total += float(repo['Avg After Commit Size'])
        during_total += float(repo['Avg During Commit Size'])

    # Calculate the average commit size using the totals above
    before_avg = before_total / len(repo_data)
    after_avg = after_total / len(repo_data)
    during_avg = during_total / len(repo_data)

    # Clear any existing plot
    plt.clf()

    # Plot the bar chart
    colors = ['palegreen', 'lightblue', 'lightskyblue']
    plt.bar(["Before", "After", "During"], [before_avg, after_avg, during_avg], align='center', color=colors)

    # Place values at the top of each bar
    for index, value in enumerate([before_avg, after_avg, during_avg]):
        plt.text(index, value+0.25, round(value, 1), ha='center')

    # Set title and axes labels
    plt.ylabel("Average Commit Size (No. of files)")
    plt.title("Average commit size when tests are created \nbefore, after and during implementation")

    # Save the plot
    _save_plot(plt, "3 - Average Commit Size")


def _create_tdd_languages_bar_graph():
    # Read data from the repo_data csv
    repo_data = file_utils.read_csv("repo_data")

    # Initialize variables to store total for each repo
    labels = ["Java", "C++", "C#", "Kotlin", "Python"]
    percentage_total = {"Java":0, "C++":0, "C#":0, "Kotlin":0, "Python":0}
    repo_count = {"Java":0, "C++":0, "C#":0, "Kotlin":0, "Python":0}

    # Iterate through each repo and update the percentage total and repo count for the respective language
    for repo in repo_data:
        language = repo['Language']
        repo_count[language] += 1
        try:
            percentage_total[language] += (int(repo['Test Before']) / (int(repo['Test Before']) + int(repo['Test After']))) * 100
        except ZeroDivisionError:
            pass

    percentage_avg = []
    for language in labels:
        percentage_avg.append((percentage_total[language] / repo_count[language]))

    # Clear any existing plot
    plt.clf()

    # Plot the bar chart
    colors = ['#66c2a5','#fc8d62','#8da0cb','#e78ac3','#a6d854']
    plt.bar(labels, percentage_avg, align='center', color=colors)

    # Place values at the top of each bar
    for index, value in enumerate(percentage_avg):
        plt.text(index, value+0.25, round(value, 1), ha='center')

    # Set title and axes labels
    plt.ylabel("TDD Percentage (%)")
    plt.xlabel("Language")
    plt.title("TDD percentage observed between programming languages")

    # Save the plot
    _save_plot(plt, "4 - Language TDD Percentage")


def _create_raw_tdd_percentage_pie():
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
        labels[i] = labels[i] + ' - ' + str(round(percentages[i], 1)) + '%'

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
    _save_plot(plt, "5 - Raw TDD Percentage")


def _create_overall_tdd_percentage_pie():
    # Read data from the author_data csv
    repo_data = file_utils.read_csv("repo_data")

    # Initialize Counters
    total = 0
    data = [0, 0]

    for repo in repo_data:
        data[0] += int(repo['Test Before'])
        data[1] += int(repo['Test After'])
        total += int(repo['Test Before']) + int(repo['Test After'])

    # Convert the data into percentages using a lambda function and map
    percentages = list(map(lambda x: x / max(1, total) * 100, data))


    # Update labels to include percentage values for each slice
    labels = ['TDD', 'Not TDD']
    for i in range(len(labels)):
        labels[i] = labels[i] + ' - ' + str(round(percentages[i], 1)) + '%'

    # Clear any existing plot
    plt.clf()

    # Plot the pie
    colors = ['palegreen', 'lightblue']
    patches, texts, x = plt.pie(percentages, colors=colors, autopct='%1.1f%%')

    # Plot the legend
    plt.legend(patches, labels, loc="upper left")

    # Set the title and specify axis setting
    plt.axis('equal')
    plt.title("Overall TDD Percentage")
    plt.rcParams["figure.figsize"] = [7.5, 4.25]
    plt.rcParams["figure.autolayout"] = True

    # Save the plot
    _save_plot(plt, "6 - Overall TDD Percentage")


def _create_tdd_author_categories_pie():
    # Read data from the author_data csv
    author_data = file_utils.read_csv("author_data")

    # Initialize Counters
    #10 25 50 70 90 100
    counters = [0,0,0,0,0,0]

    for author in author_data:
        # Calculate the percentage of TDD of the author
        # we don't count test_during as we want TDD percentage, not before, during and after percentage
        tdd_percentage = (float(author['Test Before']) / max(1, float(author['Test Before']) + float(author['Test After']))) * 100

        # Update the counters array based on this result
        counters[_get_category_index(tdd_percentage)] += 1

    # Convert the counters into percentages using a lambda function and map
    percentages = list(map(lambda x: x/max(1, len(author_data))*100, counters))

    # Update labels to include percentage values for each slice
    labels = ['Non TDD', 'Rarely TDD', 'Occasionally TDD', 'Somewhat TDD', 'Mostly TDD', 'Consistently TDD']
    for i in range(len(labels)):
        labels[i] = labels[i] + ' - ' + str(round(percentages[i], 1)) + '%'

    # Clear any existing plot
    plt.clf()

    # Plot the pie
    colors = ['#225ea8', '#1d91c0', '#41b6c4', '#7fcdbb', '#c7e9b4', '#71cb71']
    patches, texts = plt.pie(percentages, colors=colors)

    # Plot the legend
    plt.legend(patches, labels, loc="upper left")

    # Set the title and specify axis setting
    plt.axis('equal')
    plt.title("Pie chart showing levels of TDD usage by authors")
    plt.rcParams["figure.figsize"] = [7.5, 4.25]
    plt.rcParams["figure.autolayout"] = True

    # Save the plot
    _save_plot(plt, "7 - TDD Author Categories")


def _create_tdd_repo_categories_pie():
    # Read data from the author_data csv
    repo_data = file_utils.read_csv("repo_data")

    # Initialize Counters
    #10 25 50 70 90 100
    counters = [0,0,0,0,0,0]

    for repo in repo_data:
        # Calculate the percentage of TDD of the author
        # we don't count test_during as we want TDD percentage, not before, during and after percentage
        tdd_percentage = (float(repo['Test Before']) / max(1, float(repo['Test Before']) + float(repo['Test After']))) * 100

        # Update the counters array based on this result
        counters[_get_category_index(tdd_percentage)] += 1

    # Convert the counters into percentages using a lambda function and map
    percentages = list(map(lambda x: x/max(1, len(repo_data))*100, counters))

    # Update labels to include percentage values for each slice
    labels = ['Non TDD', 'Rarely TDD', 'Occasionally TDD', 'Somewhat TDD', 'Mostly TDD', 'Consistently TDD']
    for i in range(len(labels)):
        labels[i] = labels[i] + ' - ' + str(round(percentages[i], 1)) + '%'

    # Clear any existing plot
    plt.clf()

    # Plot the pie
    colors = ['#225ea8', '#1d91c0', '#41b6c4', '#7fcdbb', '#c7e9b4', '#71cb71']
    patches, texts = plt.pie(percentages, colors=colors)

    # Plot the legend
    plt.legend(patches, labels, loc="upper left")

    # Set the title and specify axis setting
    plt.axis('equal')
    plt.title("Pie chart showing levels of TDD usage seen in repositories")
    plt.rcParams["figure.figsize"] = [7.5, 4.25]
    plt.rcParams["figure.autolayout"] = True

    # Save the plot
    _save_plot(plt, "8 - TDD Repo Categories")


def create_plots():
    make_adjustments('author_data')
    make_adjustments('repo_data')
    _create_size_impact_scatter()
    _create_tdd_usage_box_plot()
    _create_avg_commit_size_bar_graph()
    _create_tdd_languages_bar_graph()
    _create_raw_tdd_percentage_pie()
    _create_overall_tdd_percentage_pie()
    _create_tdd_author_categories_pie()
    _create_tdd_repo_categories_pie()