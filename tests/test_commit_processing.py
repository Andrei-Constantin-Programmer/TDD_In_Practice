from datetime import datetime
import unittest
from unittest.mock import MagicMock, patch
from collections import defaultdict
from src.models.CustomCommit import CustomCommit
from src.models.JavaFileHandler import JavaFileHandler

from src.commit_processing import (
    gather_commits_and_tests,
    precompute_commit_map,
    find_nearest_implementation,
    calculate_average_commit_size
)

class TestCommitProcessing(unittest.TestCase):

    def setUp(self):
        self.java_file_handler = JavaFileHandler()

    def test_precompute_commit_map_with_empty_commits(self):
        # Arrange
        commits = []

        # Act
        result = precompute_commit_map(commits)

        # Assert
        self.assertEqual(result, {})

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


    @patch("commit_retrieval.read_repo_info")
    def test_gather_commits_and_tests_with_valid_data(self, mock_read_repo_info):
        # Arrange
        mock_read_repo_info.return_value = [
            MagicMock(
                hash="abc123",
                modified_files=["TestFile1.java", "File1.java"],
                author="Author1",
                date=datetime(2023, 1, 1),
            )
        ]

        # Act
        commits, test_files = gather_commits_and_tests("mock_repo", self.java_file_handler)

        # Assert
        self.assertEqual(len(commits), 1)
        self.assertEqual(len(test_files), 1)

    @patch("commit_retrieval.read_repo_info")
    def test_gather_commits_and_tests_with_no_commits(self, mock_read_repo_info):
        # Arrange
        mock_read_repo_info.return_value = []

        # Act
        commits, test_files = gather_commits_and_tests("mock_repo", self.java_file_handler)

        # Assert
        self.assertEqual(commits, [])
        self.assertEqual(test_files, [])


    def test_calculate_average_commit_size(self):
        # Arrange
        commits = {
            0: MagicMock(size=100),
            1: MagicMock(size=200),
            2: MagicMock(size=300)
        }
        test_files = [(0,), (1,), (2,)]
        
        # Act
        average_size = calculate_average_commit_size(commits, test_files)

        # Assert
        self.assertEqual(average_size, 200.0)

    def test_calculate_average_commit_size_when_no_test_files(self):
        # Arrange
        commits = {
            0: MagicMock(size=100),
            1: MagicMock(size=200),
            2: MagicMock(size=300)
        }
        test_files = []

        # Act, Assert
        with self.assertRaises(ZeroDivisionError):
            calculate_average_commit_size(commits, test_files)



if __name__ == "__main__":
    unittest.main()
