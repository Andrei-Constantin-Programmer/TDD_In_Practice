import unittest
from unittest.mock import patch, MagicMock
from src import csv_export
from src.csv_export import (
    update_author_data, 
    update_repo_data, 
    update_author_count
)

class TestCsvExport(unittest.TestCase):
    
    def setUp(self):
        self.patcher_logging = patch("src.csv_export.logging")
        self.mock_logging = self.patcher_logging.start()
        self.mock_logging.notify = MagicMock()

    def tearDown(self):
        self.patcher_logging.stop()


    @patch("repository_utils.create_or_update_csv")
    def test_update_author_data(self, mock_create_or_update_csv):
        data = ["author_name", "data1", "data2"]
        update_author_data(data)
        
        mock_create_or_update_csv.assert_called_once_with(
            csv_export.AUTHOR_CSV_PATH,
            unittest.mock.ANY, 
            data, 
            "author_name", 
            unittest.mock.ANY
        )

    @patch("repository_utils.create_or_update_csv")
    def test_update_repo_data(self, mock_create_or_update_csv):
        data = ["repo_name", "data1", "data2"]
        update_repo_data(data)
        
        mock_create_or_update_csv.assert_called_once_with(
            csv_export.REPO_CSV_PATH,
            unittest.mock.ANY, 
            data, 
            "repo_name",
        )

    def test_update_author_count(self):
        commits = {
            0: MagicMock(author="John Doe"),
            1: MagicMock(author="Jane Doe"),
            2: MagicMock(author="John Doe")
        }
        author_counts = {}
        test_files = [(0,), (1,), (2,)]
        update_author_count(commits, author_counts, test_files, index_to_update=1)

        expected_counts = {
            "John Doe": [0, 2, 0],
            "Jane Doe": [0, 1, 0]
        }
        self.assertEqual(author_counts, expected_counts)


if __name__ == "__main__":
    unittest.main()
