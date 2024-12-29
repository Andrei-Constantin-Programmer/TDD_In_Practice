import asyncio
from datetime import datetime
import logging
import timeit
from tqdm.asyncio import tqdm
import infrastructure.repository_utils as repository_utils
from models.JavaFileHandler import JavaFileHandler
from models.LanguageFileHandler import LanguageFileHandler
import commit_processing as process
import commit_retrieval as retrieval
import infrastructure.configuration as configuration
from csv_export import update_author_count, update_author_data, update_repo_data, anonymyse_authors

DATE_OF_EXPERIMENT = datetime(2024, 12, 1, 0, 0, 0)

def _categorise_test_files(test_files, commits, commit_map, file_handler):
    array_before = []
    array_after = []
    array_during = []

    for test_file in test_files:
        nearest_implementation = process.find_nearest_implementation(test_file, commits, commit_map, file_handler)
        if nearest_implementation is None:
            continue

        if test_file[0] < nearest_implementation:
            array_before.append(test_file)
        elif test_file[0] > nearest_implementation:
            array_after.append(test_file)
        else:
            array_during.append(test_file)
    
    return array_before, array_after, array_during

def _calculate_commit_metrics(commits, before, after, during):
    avg_size_before = process.calculate_average_commit_size(commits, before)
    avg_size_after = process.calculate_average_commit_size(commits, after)
    avg_size_during = process.calculate_average_commit_size(commits, during)
    avg_size_total = round((avg_size_before + avg_size_after + avg_size_during) / 3, 1)
    return avg_size_before, avg_size_after, avg_size_during, avg_size_total

def _export_data(repo_name, commits, duration, avg_sizes, before, after, during, file_handler):
    test_before = len(before)
    test_after = len(after)
    test_during = len(during)
    data_for_repo_csv = [repo_name, file_handler.name, test_before, test_after, test_during, duration, *avg_sizes]
    
    update_repo_data(data_for_repo_csv)

    author_counts = {}
    update_author_count(commits, author_counts, before, 0)
    update_author_count(commits, author_counts, after, 1)
    update_author_count(commits, author_counts, during, 2)

    for key in author_counts.keys():
        update_author_data([key] + author_counts[key])

def _process_repo(repo, file_handler):
    processing_started_message = 'Started processing ' + repo.name
    logging.notify(processing_started_message)
    start_time = timeit.default_timer()
    
    commits, test_files = process.gather_commits_and_tests(repo.name, file_handler)
    commit_map = process.precompute_commit_map(commits)
    before, after, during = _categorise_test_files(test_files, commits, commit_map, file_handler)

    avg_sizes = _calculate_commit_metrics(commits, before, after, during)
    duration = round((timeit.default_timer() - start_time), 1)
    _export_data(repo.name, commits, duration, avg_sizes, before, after, during, file_handler)

    processing_finished_message = "Finished processing " + repo.name
    logging.notify(processing_finished_message)

async def _store_repo_data(repo, file_handler):
    processing_started_message = 'Started data retrieval for ' + repo.name
    logging.notify(processing_started_message)

    await retrieval.retrieve_and_store_repo_info(repo, file_handler, final_date=DATE_OF_EXPERIMENT)

    processing_finished_message = "Finished data retrieval for " + repo.name
    logging.notify(processing_finished_message)

async def _process_repositories(file_handler: LanguageFileHandler):
    repositories = repository_utils.read_repositories(file_handler.name.lower())

    retrieval_message = "Retrieval:"
    logging.notify(retrieval_message)
    print(retrieval_message)

    tasks = [_store_repo_data(repo, file_handler) for repo in repositories]
    await tqdm.gather(*tasks)

    processing_message = "\nProcessing:"
    logging.notify(processing_message)
    print(processing_message)

    timed_list = tqdm(repositories)
    for repo in timed_list:
        _process_repo(repo, file_handler)

async def main():
    configuration.setup_directories()
    configuration.setup_logging()
    
    logging.notify("Program 'main()' has started")

    file_handlers = [JavaFileHandler()]
    for file_handler in file_handlers:
        await _process_repositories(file_handler)

    anonymyse_authors()

if __name__ == "__main__":
    asyncio.run(main())
