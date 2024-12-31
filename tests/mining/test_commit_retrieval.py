import asyncio
import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.models.JavaFileHandler import JavaFileHandler
from src.models.Repository import Repository
from src.infrastructure import file_utils

from src.mining.commit_retrieval import (
    retrieve_and_store_repo_info,
    read_repo_info,
)

class TestCommitRetrieval(unittest.TestCase):

    def setUp(self):
        self.java_file_handler = JavaFileHandler()
        self.repo = Repository(name="mock_repo", url="https://mock-repo.git")

    @patch("src.infrastructure.file_utils.file_exists", return_value=False)
    @patch("src.infrastructure.serialize.serialize")
    @patch("src.infrastructure.repository_utils.read_commits")
    def test_retrieve_and_store_repo_info_with_no_modified_files(self, mock_read_commits, mock_serialize, mock_file_exists):
        # Arrange
        test_date = datetime(2023, 1, 1)
        mock_read_commits.return_value = [
            MagicMock(hash="abc123", modified_files=[], author="Author1", author_date=test_date)
        ]

        # Act
        with patch("asyncio.to_thread", side_effect=lambda func, *args: func(*args)):
            asyncio.run(retrieve_and_store_repo_info(self.repo, self.java_file_handler))

        # Assert
        mock_read_commits.assert_called_once_with("https://mock-repo.git", None)
        mock_serialize.assert_called_once()
        commits = mock_serialize.call_args[0][1]
        self.assertEqual(len(commits), 1)
        self.assertEqual(len(commits[0].modified_files), 0)

    @patch("src.infrastructure.file_utils.file_exists", return_value=False)
    @patch("src.infrastructure.serialize.serialize")
    @patch("src.infrastructure.repository_utils.read_commits")
    def test_retrieve_and_store_repo_info_with_final_date(self, mock_read_commits, mock_serialize, mock_file_exists):
        # Arrange
        final_date = datetime(2024, 1, 1)
        mock_read_commits.return_value = [
            MagicMock(hash="abc123", modified_files=[MagicMock(filename="TestFile1.java")], author="Author1", author_date=final_date)
        ]

        # Act
        with patch("asyncio.to_thread", side_effect=lambda func, *args: func(*args)):
            asyncio.run(retrieve_and_store_repo_info(self.repo, self.java_file_handler, final_date))

        # Assert
        mock_read_commits.assert_called_once_with("https://mock-repo.git", final_date)
        mock_serialize.assert_called_once()
        commits = mock_serialize.call_args[0][1]
        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0].hash, "abc123")

    @patch("src.infrastructure.file_utils.file_exists", return_value=False)
    @patch("src.infrastructure.serialize.serialize")
    @patch("src.infrastructure.repository_utils.read_commits")
    def test_retrieve_and_store_repo_info_with_commits_without_files(self, mock_read_commits, mock_serialize, mock_file_exists):
        # Arrange
        test_date = datetime(2023, 1, 1)
        mock_read_commits.return_value = [
            MagicMock(hash="abc123", modified_files=[], author="Author1", author_date=test_date),
            MagicMock(hash="def456", modified_files=[], author="Author2", author_date=test_date),
        ]

        # Act
        with patch("asyncio.to_thread", side_effect=lambda func, *args: func(*args)):
            asyncio.run(retrieve_and_store_repo_info(self.repo, self.java_file_handler))

        # Assert
        mock_read_commits.assert_called_once_with("https://mock-repo.git", None)
        mock_serialize.assert_called_once()
        commits = mock_serialize.call_args[0][1]
        self.assertEqual(len(commits), 2)
        self.assertEqual(len(commits[0].modified_files), 0)
        self.assertEqual(commits[0].hash, "abc123")
        self.assertEqual(len(commits[1].modified_files), 0)
        self.assertEqual(commits[1].hash, "def456")

    @patch("src.infrastructure.file_utils.file_exists", return_value=False)
    @patch("src.infrastructure.serialize.serialize")
    @patch("src.infrastructure.repository_utils.read_commits")
    @patch("src.infrastructure.repository_utils.logging.error")
    def test_retrieve_and_store_repo_info_with_failing_commit_generator(self, mock_logging_error, mock_read_commits, mock_serialize, mock_file_exists):
        # Arrange
        mock_read_commits.side_effect = Exception("Test exception")
        
        # Act
        with patch("asyncio.to_thread", side_effect=lambda func, *args: func(*args)):
            asyncio.run(retrieve_and_store_repo_info(self.repo, self.java_file_handler))

        # Assert
        mock_read_commits.assert_called_once_with("https://mock-repo.git", None)
        mock_logging_error.assert_called_once_with(f"Could not drill repository {self.repo.url}: Test exception")
        mock_serialize.assert_not_called()


    @patch("src.infrastructure.serialize.deserialize")
    def test_read_repo_info_with_commits(self, mock_deserialize):
        # Arrange
        mock_commits = [
            MagicMock(hash="abc123", modified_files=["TestFile1.java"], author="Author1", author_date="2023-01-01"),
            MagicMock(hash="def456", modified_files=["TestFile2.java"], author="Author2", author_date="2023-01-02"),
        ]
        mock_deserialize.return_value = mock_commits

        # Act
        result = read_repo_info("mock_repo")

        # Assert
        mock_deserialize.assert_called_once_with(os.path.join(file_utils.COMMITS_PATH, "mock_repo.pkl"))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].hash, "abc123")
        self.assertEqual(result[1].hash, "def456")
        
    @patch("src.infrastructure.serialize.deserialize")
    def test_read_repo_info_with_empty_commits(self, mock_deserialize):
        # Arrange
        mock_deserialize.return_value = []

        # Act
        result = read_repo_info("mock_repo")

        # Assert
        mock_deserialize.assert_called_once_with(os.path.join(file_utils.COMMITS_PATH, "mock_repo.pkl"))
        self.assertEqual(result, [])

    @patch("src.infrastructure.serialize.deserialize")
    @patch("logging.warning")
    def test_read_repo_info_with_commits(self, mock_logging_warning, mock_deserialize):
        # Arrange
        mock_deserialize.side_effect = Exception("Test exception")

        # Act
        result = read_repo_info("mock_repo")

        # Assert
        mock_deserialize.assert_called_once_with(os.path.join(file_utils.COMMITS_PATH, "mock_repo.pkl"))
        self.assertEqual(len(result), 0)
        mock_logging_warning.assert_called_once()


if __name__ == "__main__":
    unittest.main()