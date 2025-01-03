import asyncio
import logging
import timeit
from datetime import datetime
from tqdm.asyncio import tqdm
from src.infrastructure import repository_utils as repository_utils
from src.models import LanguageFileHandler
from src.mining import commit_processing as process
from src.mining import commit_retrieval as retrieval
from src.mining.csv_export import update_author_count, update_author_data, update_repo_data, anonymyse_authors
from src.models.Repository import Repository

class AnalysisManager():
    def __init__(self, date_of_experiment: datetime):
        self.date_of_experiment = date_of_experiment
        

    def _categorise_test_files(self, test_files, commits, commit_map, file_handler):
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

    def _calculate_commit_metrics(self, commits, before, after, during):
        avg_size_before = process.calculate_average_commit_size(commits, before)
        avg_size_after = process.calculate_average_commit_size(commits, after)
        avg_size_during = process.calculate_average_commit_size(commits, during)
        avg_size_total = round((avg_size_before + avg_size_after + avg_size_during) / 3, 1)
        return avg_size_before, avg_size_after, avg_size_during, avg_size_total

    def _export_data(self, repo_name, commits, duration, avg_sizes, before, after, during, file_handler):
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

    def process_repo(self, repo, file_handler):
        processing_started_message = 'Started processing ' + repo.name
        logging.notify(processing_started_message)
        start_time = timeit.default_timer()
        
        commits, test_files = process.gather_commits_and_tests(repo.name, file_handler)
        if len(test_files) == 0:
            logging.notify(f"No test files found for {repo.name}. Skipping...")
            return

        commit_map = process.precompute_commit_map(commits)
        before, after, during = self._categorise_test_files(test_files, commits, commit_map, file_handler)

        avg_sizes = self._calculate_commit_metrics(commits, before, after, during)
        duration = round((timeit.default_timer() - start_time), 1)
        self._export_data(repo.name, commits, duration, avg_sizes, before, after, during, file_handler)

        processing_finished_message = "Finished processing " + repo.name
        logging.notify(processing_finished_message)

    async def _store_repo_data(self, repo, file_handler, force_mine):
        processing_started_message = 'Started data retrieval for ' + repo.name
        logging.notify(processing_started_message)

        await retrieval.retrieve_and_store_repo_info(repo, file_handler, final_date=self.date_of_experiment, force_mine=force_mine)

        processing_finished_message = "Finished data retrieval for " + repo.name
        logging.notify(processing_finished_message)

    async def _process_repositories(self, repositories, file_handler: LanguageFileHandler, batch_size: int, force_mine: bool):
        retrieval_message = "Retrieval:"
        logging.notify(retrieval_message)
        print(retrieval_message)

        with tqdm(total=len(repositories)) as progress_bar:
            async def process_and_update(repo):
                await self._store_repo_data(repo, file_handler, force_mine)
                progress_bar.update(1)

            for i in range(0, len(repositories), batch_size):
                repo_batch = repositories[i:i + batch_size]
                tasks = [process_and_update(repo) for repo in repo_batch]
                await asyncio.gather(*tasks)

        processing_message = "\nProcessing:"
        logging.notify(processing_message)
        print(processing_message)

        timed_list = tqdm(repositories)
        for repo in timed_list:
            self.process_repo(repo, file_handler)

    async def perform_analysis_on_repo(self, repo: Repository, file_handler: LanguageFileHandler, force_mine: bool):
        await self._process_repositories([repo], file_handler, batch_size=1, force_mine=force_mine)
        anonymyse_authors()

    async def perform_analysis(self, file_handlers: list, batch_size: int, force_mine: bool):
        for file_handler in file_handlers:
            repositories = repository_utils.read_repositories(file_handler.name.lower())
            await self._process_repositories(repositories, file_handler, batch_size, force_mine)

        anonymyse_authors()