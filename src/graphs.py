import os
from matplotlib import pyplot as plt


def plot_bar_graph(test_before, test_during, test_after, repo):
    """
    Function to plot a bar chart showing the order of commits for test files
    @param test_before: An Integer representing the number of tests that were committed BEFORE their corresponding implementation
    @param test_during: An Integer representing the number of tests that were committed TOGETHER with their corresponding implementation
    @param test_after: An Integer representing the number of tests that were committed AFTER their corresponding implementation
    @param repo: A String representing the repository which we will search and retrieve commits from
    """
    # Specify the bars names
    categories = ['Test Before Impl.', 'Same Time', 'Impl. Before Test']
    # Match the values for each bar
    values = [test_before, test_during, test_after]
    # Give each bar a different color
    plt.bar(categories, values, color=["#1984c5", "#22a7f0", "#63bff0"])
    # Assign the plot a title, x, and y label
    plt.title('Test and Implementation commit order. Repo: ' + repo)
    plt.xlabel('Test/Implementation Commit Order')
    plt.ylabel('Number of Test/Implementation Pairs')
    # Basic Formatting
    plt.xticks(rotation=45)
    plt.tight_layout()
    # Save the plot
    output_dir = "./../plots/"
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(output_dir + repo + "_plot.jpg")
    
    plt.show()