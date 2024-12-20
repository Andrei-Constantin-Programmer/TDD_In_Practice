from datetime import datetime
import unittest
from unittest.mock import MagicMock, patch
from collections import defaultdict
from src.models.CustomCommit import CustomCommit
from src.models.JavaFileHandler import JavaFileHandler

from src.commit_processing import (
    retrieve_files,
    retrieve_commits,
    gather_commits_and_tests,
    precompute_commit_map,
    find_nearest_implementation,
)

class TestCommitProcessing(unittest.TestCase):

    def setUp(self):
        self.java_file_handler = JavaFileHandler()

    def test_retrieve_files_with_java_files(self):
        # Arrange
        mock_modified_files = [
            MagicMock(filename="TestFile1.java"),
            MagicMock(filename="TestFile2.py"),
            MagicMock(filename="TestFile3.java"),
        ]

        # Act
        result = retrieve_files(mock_modified_files, self.java_file_handler)

        # Assert
        self.assertEqual(result, ["TestFile1.java", "TestFile3.java"])

    def test_retrieve_files_with_no_java_files(self):
        # Arrange
        mock_modified_files = [
            MagicMock(filename="TestFile1.py"),
            MagicMock(filename="TestFile2.txt"),
        ]

        # Act
        result = retrieve_files(mock_modified_files, self.java_file_handler)

        # Assert
        self.assertEqual(result, [])

    def test_retrieve_files_with_empty_modified_files(self):
        # Arrange
        mock_modified_files = []

        # Act
        result = retrieve_files(mock_modified_files, self.java_file_handler)

        # Assert
        self.assertEqual(result, [])


    @patch("repository_utils.read_commits")
    def test_retrieve_commits_with_valid_commits(self, mock_read_commits):
        # Arrange
        test_date = datetime(2023, 1, 1)
        mock_read_commits.return_value = [
            MagicMock(
                hash="abc123",
                modified_files=[MagicMock(filename="TestFile1.java")],
                author="Author1",
                author_date=test_date,
            )
        ]

        # Act
        result = retrieve_commits("mock_repo", self.java_file_handler)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0].modified_files), 1)
        self.assertEqual(result[0].hash, "abc123")
        self.assertEqual(result[0].author, "Author1")
        self.assertEqual(result[0].date, test_date)

    @patch("repository_utils.read_commits")
    def test_retrieve_commits_with_final_date(self, mock_read_commits):
        # Arrange
        mock_read_commits.return_value = [
            MagicMock(
                hash="abc123",
                modified_files=[MagicMock(filename="TestFile1.java")],
                author="Author1",
                author_date=datetime(2023, 1, 1),
            )
        ]

        final_date = datetime(2024, 1, 1, 0, 0, 0)

        # Act
        _ = retrieve_commits("mock_repo", self.java_file_handler, final_date)

        # Assert
        mock_read_commits.assert_called_once_with("mock_repo", final_date)

    @patch("repository_utils.read_commits", return_value=[])
    def test_retrieve_commits_with_no_commits(self, _):
        # Act
        result = retrieve_commits("mock_repo", self.java_file_handler)

        # Assert
        self.assertEqual(result, [])


    def test_precompute_commit_map_with_multiple_files(self):
        # Arrange
        commits = [
            CustomCommit("hash1", ["FileA.java"], "Author1", datetime(2023, 1, 1)),
            CustomCommit("hash2", ["FileB.java", "FileC.java"], "Author2", datetime(2023, 1, 2)),
            CustomCommit("hash3", ["FileA.java", "FileC.java"], "Author3", datetime(2023, 1, 3)),
        ]

        # Act
        result = precompute_commit_map(commits)

        # Assert
        self.assertEqual(result["FileA.java"], [0, 2])
        self.assertEqual(result["FileB.java"], [1])
        self.assertEqual(result["FileC.java"], [1, 2])

    def test_precompute_commit_map_with_no_files(self):
        # Arrange
        commits = [
            CustomCommit("hash1", [], "Author1", datetime(2023, 1, 1)),
            CustomCommit("hash2", [], "Author2", datetime(2023, 1, 2)),
        ]

        # Act
        result = precompute_commit_map(commits)

        # Assert
        self.assertEqual(result, {})


    def test_find_nearest_implementation_with_no_candidates(self):
        # Arrange
        commits = [
            CustomCommit("hash1", ["TestFile.java"], "Author1", datetime(2023, 1, 1)),
            CustomCommit("hash2", ["Implementation.java"], "Author2", datetime(2023, 1, 2)),
        ]
        test_file = (0, "TestFile.java")
        commit_map = defaultdict(list)

        # Act
        result = find_nearest_implementation(test_file, commits, commit_map, self.java_file_handler)

        # Assert
        self.assertIsNone(result)

    def test_find_nearest_implementation_with_only_after_candidates(self):
        # Arrange
        commits = [
            CustomCommit("hash1", ["TestFile.java"], "Author1", datetime(2023, 1, 1)),
            CustomCommit("hash2", ["File.java"], "Author2", datetime(2023, 1, 2)),
            CustomCommit("hash3", ["File.java"], "Author3", datetime(2023, 1, 3)),
        ]
        test_file = (0, "TestFile.java")
        commit_map = defaultdict(list, {"File.java": [1, 2]})

        # Act
        result = find_nearest_implementation(test_file, commits, commit_map, self.java_file_handler)

        # Assert
        self.assertEqual(result, 1)

    def test_find_nearest_implementation_with_only_before_candidates(self):
        # Arrange
        commits = [
            CustomCommit("hash1", ["TestFile.java"], "Author1", datetime(2023, 1, 1)),
            CustomCommit("hash2", ["File.java"], "Author2", datetime(2023, 1, 2)),
            CustomCommit("hash3", ["File.java"], "Author3", datetime(2023, 1, 3)),
        ]
        test_file = (2, "TestFile.java")
        commit_map = defaultdict(list, {"File.java": [0, 1]})

        # Act
        result = find_nearest_implementation(test_file, commits, commit_map, self.java_file_handler)

        # Assert
        self.assertEqual(result, 1)


    @patch("repository_utils.read_commits")
    def test_gather_commits_and_tests_with_valid_data(self, mock_read_commits):
        # Arrange
        mock_read_commits.return_value = [
            MagicMock(
                hash="abc123",
                modified_files=[MagicMock(filename="TestFile1.java"), MagicMock(filename="File1.java")],
                author="Author1",
                date=datetime(2023, 1, 1),
            )
        ]

        # Act
        commits, test_files = gather_commits_and_tests("mock_repo", self.java_file_handler)

        # Assert
        self.assertEqual(len(commits), 1)
        self.assertEqual(len(test_files), 1)

    @patch("repository_utils.read_commits")
    def test_gather_commits_and_tests_with_no_commits(self, mock_read_commits):
        # Arrange
        mock_read_commits.return_value = []  # Mock read_commits to return an empty list

        # Act
        commits, test_files = gather_commits_and_tests("mock_repo", self.java_file_handler)

        # Assert
        # Ensure that the returned commits and test files are empty
        self.assertEqual(commits, [])
        self.assertEqual(test_files, [])

    @patch("repository_utils.read_commits")
    def test_gather_commits_and_tests_with_final_date(self, mock_read_commits):
        # Arrange
        mock_read_commits.return_value = [
            MagicMock(
                hash="abc123",
                modified_files=[MagicMock(filename="TestFile1.java"), MagicMock(filename="File1.java")],
                author="Author1",
                date=datetime(2023, 1, 1),
            )
        ]
        final_date = datetime(2024, 1, 1, 0, 0, 0)

        # Act
        _ = gather_commits_and_tests("mock_repo", self.java_file_handler, final_date=final_date)

        # Assert
        mock_read_commits.assert_called_once_with("mock_repo", final_date)


if __name__ == "__main__":
    unittest.main()
