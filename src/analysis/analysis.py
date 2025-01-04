from distutils.dep_util import newer_pairwise
from idlelib.colorizer import color_config

from PIL.ImageColor import colormap

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


create_size_impact_plot()
create_box_plot()

'''

8. How does TDD adoption vary between projects?

'''


