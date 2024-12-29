import os
import unittest
from unittest.mock import mock_open, patch
import unittest.mock

from src.infrastructure import file_utils
from src.infrastructure.file_utils import (
    create_directory,
    file_exists,
    read_csv,
    write_csv,
    create_or_update_csv,
)

class TestFileUtils(unittest.TestCase):

    @patch("src.infrastructure.file_utils.os.makedirs")
    def test_create_directory_new(self, mock_makedirs):
        # Act
        path = create_directory("test_path")

        # Assert
        mock_makedirs.assert_called_once_with("test_path", exist_ok=True)
        self.assertEqual(path, "test_path")

    @patch("src.infrastructure.file_utils.shutil.rmtree")
    @patch("src.infrastructure.file_utils.os.makedirs")
    @patch("src.infrastructure.file_utils.os.path.exists", return_value=True)
    def test_create_directory_existing(self, mock_exists, mock_makedirs, mock_rmtree):
        # Act
        path = create_directory("test_path", delete_existing=True)

        # Assert
        mock_exists.assert_called_once_with("test_path")
        mock_rmtree.assert_called_once_with("test_path")
        mock_makedirs.assert_called_once_with("test_path", exist_ok=False)
        self.assertEqual(path, "test_path")

    @patch("src.infrastructure.file_utils.os.path.isfile", return_value=True)
    def test_file_exists_true(self, _):
        # Act
        result = file_exists("test_file.txt")

        # Assert
        self.assertTrue(result)

    @patch("src.infrastructure.file_utils.os.path.isfile", return_value=False)
    def test_file_exists_false(self, _):
        # Act
        result = file_exists("test_file.txt")

        # Assert
        self.assertFalse(result)

    @patch("src.infrastructure.file_utils.file_exists", return_value=False)
    def test_read_csv_file_not_found(self, _):
        # Act & Assert
        with self.assertRaises(FileNotFoundError):
            read_csv("test_file")

    @patch("src.infrastructure.file_utils.open", new_callable=mock_open, read_data="header1,header2\nvalue1,value2\n")
    @patch("src.infrastructure.file_utils.file_exists", return_value=True)
    def test_read_csv_file_found(self, _, mock_open_file):
        # Act
        result = read_csv("test_file")

        # Assert
        mock_open_file.assert_called_once_with(os.path.join(file_utils.RESULTS_PATH, "test_file.csv"), "r", encoding=unittest.mock.ANY)
        self.assertEqual(result, [{"header1": "value1", "header2": "value2"}])

    @patch("src.infrastructure.file_utils.os.makedirs")
    @patch("src.infrastructure.file_utils.open", new_callable=mock_open)
    def test_write_csv(self, mock_open_file, mock_makedirs):
        # Arrange
        content = [["header1", "header2"], ["value1", "value2"]]

        # Act
        write_csv(content, "test_file")

        # Assert
        mock_makedirs.assert_called_once_with(file_utils.RESULTS_PATH, exist_ok=True)
        mock_open_file.assert_called_once_with(os.path.join(file_utils.RESULTS_PATH, "test_file.csv"), mode="w", encoding=unittest.mock.ANY, newline=unittest.mock.ANY)
        mock_open_file().write.assert_called()

    def test_write_csv_invalid_content(self):
        # Arrange
        content = "Invalid Content"

        # Act & Assert
        with self.assertRaises(ValueError):
            write_csv(content, "test_file")

    @patch("src.infrastructure.file_utils.file_exists", return_value=False)
    @patch("src.infrastructure.file_utils.open", new_callable=mock_open)
    def test_create_or_update_csv_new_file(self, mock_open_file, _):
        # Arrange
        file_path = "test.csv"
        headers = ["id", "value"]
        data = ["1", "test_value"]

        # Act
        create_or_update_csv(file_path, headers, data, "1")

        # Assert
        mock_open_file.assert_called_with(file_path, "w", newline="", encoding="utf-8")
        mock_open_file().write.assert_called()

    @patch("src.infrastructure.file_utils.file_exists", return_value=True)
    @patch("src.infrastructure.file_utils.open", new_callable=mock_open, read_data="id,value\n1,old_value\n")
    def test_create_or_update_csv_update_row(self, mock_open_file, _):
        # Arrange
        file_path = "test.csv"
        headers = ["id", "value"]
        data = ["1", "new_value"]

        # Act
        create_or_update_csv(file_path, headers, data, "1")

        # Assert
        mock_open_file.assert_called_with(file_path, "w", newline="", encoding="utf-8")
        mock_open_file().write.assert_called()

    @patch("src.infrastructure.file_utils.file_exists", return_value=True)
    @patch("src.infrastructure.file_utils.open", new_callable=mock_open, read_data="id,value\n1,old_value\n")
    def test_create_or_update_csv_add_row(self, mock_open_file, _):
        # Arrange
        file_path = "test.csv"
        headers = ["id", "value"]
        data = ["2", "new_value"]

        # Act
        create_or_update_csv(file_path, headers, data, "2")

        # Assert
        mock_open_file.assert_called_with(file_path, "w", newline="", encoding="utf-8")
        mock_open_file().write.assert_called()


if __name__ == "__main__":
    unittest.main()