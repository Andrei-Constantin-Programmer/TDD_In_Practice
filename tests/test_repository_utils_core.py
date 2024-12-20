from datetime import datetime, timedelta
import unittest
from unittest.mock import MagicMock, mock_open, patch
from src.repository_utils_core import read_repository_names, read_csv, write_csv, read_commits

class TestRepositoryUtilsCore(unittest.TestCase):
    def test_read_repository_names(self):
        # Arrange
        mock_file_content = "repo1\nrepo2\nrepo3"
        file_like = mock_open(read_data=mock_file_content)()

        # Act
        result = read_repository_names(file_like)

        # Assert
        self.assertEqual(result, [
            "https://github.com/apache/repo1.git",
            "https://github.com/apache/repo2.git",
            "https://github.com/apache/repo3.git"
        ])

    def test_read_csv(self):
        # Arrange
        mock_csv_content = "col1,col2\nval1,val2\nval3,val4"
        file_like = mock_open(read_data=mock_csv_content)()

        # Act
        result = read_csv(file_like)

        # Assert
        self.assertEqual(result, [
            {"col1": "val1", "col2": "val2"},
            {"col1": "val3", "col2": "val4"}
        ])

    def test_write_csv(self):
        # Arrange
        content = [["col1", "col2"], ["val1", "val2"], ["val3", "val4"]]
        mock_file = mock_open()
        file_like = mock_file()

        # Act
        write_csv(content, file_like)

        # Assert
        handle = file_like
        handle.write.assert_any_call("col1,col2\r\n")
        handle.write.assert_any_call("val1,val2\r\n")
        handle.write.assert_any_call("val3,val4\r\n")

    @patch("src.repository_utils_core.Repository")
    @patch("src.repository_utils_core.datetime")
    def test_read_commits(self, mock_datetime, mock_repository):
        # Arrange
        fake_now = datetime(2024, 12, 12, 0, 0, 0)

        repo_url = "https://github.com/apache/repo1.git"
        mock_commit = MagicMock()
        mock_commit.hash = "abc123"
        mock_commit.msg = "Initial commit"
        mock_commit.author_date = "2024-12-11"
        mock_repository.return_value.traverse_commits.return_value = [mock_commit]
        mock_datetime.now.return_value = fake_now

        # Act
        result = list(read_commits(repo_url))

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].hash, "abc123")
        self.assertEqual(result[0].msg, "Initial commit")
        self.assertEqual(result[0].author_date, "2024-12-11")
        mock_repository.assert_called_once_with(repo_url, only_modifications_with_file_types=['.java'], to=fake_now)

    @patch("src.repository_utils_core.Repository")
    @patch("src.repository_utils_core.datetime")
    def test_read_commits_with_no_commits_in_the_past(self, mock_datetime, mock_repository):
        # Arrange
        fake_now = datetime(2024, 1, 1, 0, 0, 0)

        repo_url = "https://github.com/apache/repo1.git"
        mock_repository.return_value.traverse_commits.return_value = []
        mock_datetime.now.return_value = fake_now

        # Act
        result = list(read_commits(repo_url))

        # Assert
        self.assertEqual(len(result), 0)

    @patch("src.repository_utils_core.Repository")
    @patch("src.repository_utils_core.datetime")
    def test_read_commits_when_datetime_is_in_the_future(self, mock_datetime, mock_repository):
        # Arrange
        fake_now = datetime(2024, 12, 12, 0, 0, 0)
        fake_tomorrow = fake_now + timedelta(days=1)

        repo_url = "https://github.com/apache/repo1.git"
        mock_commit = MagicMock()
        mock_commit.hash = "abc123"
        mock_commit.msg = "Initial commit"
        mock_commit.author_date = "2024-12-11"
        mock_repository.return_value.traverse_commits.return_value = [mock_commit]
        mock_datetime.now.return_value = fake_now

        # Act, Assert
        with self.assertRaises(ValueError):
            _ = list(read_commits(repo_url, fake_tomorrow))

    @patch("src.repository_utils_core.Repository")
    @patch("src.repository_utils_core.datetime")
    def test_read_commits_when_datetime_is_correct(self, mock_datetime, mock_repository):
        # Arrange
        fake_now = datetime(2024, 12, 15, 0, 0, 0)
        test_date = datetime(2024, 12, 12, 0, 0, 0)

        repo_url = "https://github.com/apache/repo1.git"
        mock_commit = MagicMock(hash="abc123", msg="Initial commit", author_date="2024-12-11")
        mock_repository.return_value.traverse_commits.return_value = [mock_commit]
        mock_datetime.now.return_value = fake_now

        # Act
        result = list(read_commits(repo_url, test_date))

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].hash, "abc123")
        mock_repository.assert_called_once_with(repo_url, only_modifications_with_file_types=['.java'], to=test_date)


if __name__ == "__main__":
    unittest.main()
