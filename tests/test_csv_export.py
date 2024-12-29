import unittest
from unittest.mock import patch, MagicMock
import unittest.mock
from src import csv_export
from src.csv_export import (
    update_author_data, 
    update_repo_data, 
    update_author_count,
    anonymyse_authors
)

class TestCsvExport(unittest.TestCase):
    
    def setUp(self):
        self.patcher_logging = patch("src.csv_export.logging")
        self.mock_logging = self.patcher_logging.start()
        self.mock_logging.notify = MagicMock()

    def tearDown(self):
        self.patcher_logging.stop()


    @patch("csv_export.repository_utils.create_or_update_csv")
    def test_update_author_data(self, mock_create_or_update_csv):
        # Arrange
        data = ["author_name", "data1", "data2"]

        # Act
        update_author_data(data)
        
        # Assert
        mock_create_or_update_csv.assert_called_once_with(
            csv_export.AUTHOR_CSV_PATH,
            unittest.mock.ANY, 
            data, 
            "author_name", 
            unittest.mock.ANY
        )

    @patch("csv_export.repository_utils.create_or_update_csv")
    def test_update_repo_data(self, mock_create_or_update_csv):
        # Arrange
        data = ["repo_name", "data1", "data2"]

        # Act
        update_repo_data(data)
        
        # Assert
        mock_create_or_update_csv.assert_called_once_with(
            csv_export.REPO_CSV_PATH,
            unittest.mock.ANY, 
            data, 
            "repo_name",
        )

    def test_update_author_count(self):
        # Arrange
        commits = {
            0: MagicMock(author="John Doe"),
            1: MagicMock(author="Jane Doe"),
            2: MagicMock(author="John Doe")
        }
        author_counts = {}
        test_files = [(0,), (1,), (2,)]

        expected_counts = {
            "John Doe": [0, 2, 0],
            "Jane Doe": [0, 1, 0]
        }

        # Act
        update_author_count(commits, author_counts, test_files, index_to_update=1)

        # Assert
        self.assertEqual(author_counts, expected_counts)

    @patch('csv_export.repository_utils.read_csv')
    @patch('csv_export.repository_utils.write_csv')
    def test_anonymyse_authors_single_authors(self, mock_write_csv, mock_read_csv):
        # Arrange
        mock_read_csv.return_value = [{"Author": "Alice", "Test Before": "5", "Test After": "3", "Test During": "2"}]

        expected_data = [csv_export.AUTHOR_HEADER, ["1", "5", "3", "2"]]

        # Act
        anonymyse_authors()

        # Assert
        mock_write_csv.assert_called_once_with(expected_data, 'author_data')

    @patch('csv_export.repository_utils.read_csv')
    @patch('csv_export.repository_utils.write_csv')
    def test_anonymyse_authors_multiple_authors(self, mock_write_csv, mock_read_csv):
        # Arrange
        mock_read_csv.return_value = [
            {"Author": "Alice", "Test Before": "5", "Test After": "3", "Test During": "2"},
            {"Author": "Bob", "Test Before": "8", "Test After": "2", "Test During": "1"},
            {"Author": "Charlie", "Test Before": "2", "Test After": "6", "Test During": "4"}
        ]

        expected_data = [
            csv_export.AUTHOR_HEADER,
            ["1", "5", "3", "2"],
            ["2", "8", "2", "1"],
            ["3", "2", "6", "4"]
        ]

        # Act
        anonymyse_authors()

        # Assert
        mock_write_csv.assert_called_once_with(expected_data, 'author_data')

    @patch('csv_export.repository_utils.read_csv')
    @patch('csv_export.repository_utils.write_csv')
    def test_anonymyse_authors_empty_csv(self, mock_write_csv, mock_read_csv):
        # Arrange
        mock_read_csv.return_value = []

        # Act
        anonymyse_authors()

        # Assert
        mock_write_csv.assert_not_called()


if __name__ == "__main__":
    unittest.main()
