from datetime import datetime, timedelta
import unittest
from unittest.mock import MagicMock, mock_open, patch
from src.models.Repository import Repository

from src.infrastructure.repository_utils import (
    read_repositories, 
    read_commits,
    repo_from_url,
    apache_repo_from_name
)
    
class TestRepositoryUtils(unittest.TestCase):

    @patch("src.infrastructure.repository_utils.os.path.exists", return_value=True)
    @patch("src.infrastructure.repository_utils.open", new_callable=mock_open, read_data="repo1\nrepo2\nrepo3")
    def test_read_repositories(self, _, __):
        # Arrange
        expected_repos = [
            Repository("repo1", "https://github.com/apache/repo1.git"),
            Repository("repo2", "https://github.com/apache/repo2.git"),
            Repository("repo3", "https://github.com/apache/repo3.git")
        ]

        # Act
        result = read_repositories("java")

        # Assert
        self.assertEqual(len(result), len(expected_repos))
        for actual, expected in zip(result, expected_repos):
            self.assertEqual(actual.name, expected.name)
            self.assertEqual(actual.url, expected.url)

    @patch("src.infrastructure.repository_utils.DrillerRepo")
    @patch("src.infrastructure.repository_utils.datetime")
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

    @patch("src.infrastructure.repository_utils.DrillerRepo")
    @patch("src.infrastructure.repository_utils.datetime")
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

    @patch("src.infrastructure.repository_utils.DrillerRepo")
    @patch("src.infrastructure.repository_utils.datetime")
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

    @patch("src.infrastructure.repository_utils.DrillerRepo")
    @patch("src.infrastructure.repository_utils.datetime")
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

    
    def test_repo_from_url_valid(self):
        # Arrange
        valid_url = "https://github.com/apache/test-repo.git"
        expected_repo = Repository(name="test-repo", url=valid_url)

        # Act
        result = repo_from_url(valid_url)

        # Assert
        self.assertEqual(result.name, expected_repo.name)
        self.assertEqual(result.url, expected_repo.url)

    def test_repo_from_url_invalid(self):
        # Arrange
        invalid_url = "https://example.com/apache/test-repo.git"

        # Act, Assert
        with self.assertRaises(ValueError):
            repo_from_url(invalid_url)

    def test_apache_repo_from_name(self):
        # Arrange
        repo_name = "test-repo"
        expected_url = "https://github.com/apache/test-repo.git"
        expected_repo = Repository(name=repo_name, url=expected_url)

        # Act
        result = apache_repo_from_name(repo_name)

        # Assert
        self.assertEqual(result.name, expected_repo.name)
        self.assertEqual(result.url, expected_repo.url)


if __name__ == "__main__":
    unittest.main()
