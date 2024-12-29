import asyncio
import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.models.JavaFileHandler import JavaFileHandler
from src.models.Repository import Repository
from src.infrastructure import repository_utils

from src.commit_retrieval import (
    retrieve_and_store_repo_info,
    read_repo_info,
)

class TestCommitRetrieval(unittest.TestCase):

    def setUp(self):
        self.java_file_handler = JavaFileHandler()
        self.repo = Repository(name="mock_repo", url="https://mock-repo.git")

    @patch("infrastructure.repository_utils.file_exists", return_value=False)
    @patch("infrastructure.repository_utils.serialize")
    @patch("infrastructure.repository_utils.read_commits")
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

    @patch("infrastructure.repository_utils.file_exists", return_value=False)
    @patch("infrastructure.repository_utils.serialize")
    @patch("infrastructure.repository_utils.read_commits")
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

    @patch("infrastructure.repository_utils.file_exists", return_value=False)
    @patch("infrastructure.repository_utils.serialize")
    @patch("infrastructure.repository_utils.read_commits")
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

    @patch("infrastructure.repository_utils.deserialize")
    def test_read_repo_info_with_empty_commits(self, mock_deserialize):
        # Arrange
        mock_deserialize.return_value = []

        # Act
        result = read_repo_info("mock_repo")

        # Assert
        mock_deserialize.assert_called_once_with(os.path.join(repository_utils.COMMITS_PATH, "mock_repo.pkl"))
        self.assertEqual(result, [])