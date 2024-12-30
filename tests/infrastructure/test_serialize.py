import unittest
from unittest.mock import mock_open, patch

from src.infrastructure.serialize import (
    serialize,
    deserialize
)

class TestSerialize(unittest.TestCase):
    
    @patch("src.infrastructure.serialize.open")
    @patch("src.infrastructure.serialize.pickle")
    def test_serialize(self, mock_pickle, _):
        # Arrange
        data = "Test Data"

        # Act
        serialize("path", data)

        # Assert
        mock_pickle.dump.assert_called_once_with(data, unittest.mock.ANY)
    
    @patch("src.infrastructure.serialize.file_utils.file_exists", return_value=False)
    def test_deserialize_file_not_exist(self, mock_file_exists):
        # Arrange
        file_path = "non_existent_file.pkl"

        # Act & Assert
        with self.assertRaises(FileNotFoundError):
            deserialize(file_path)
        
        mock_file_exists.assert_called_once_with(file_path)

    @patch("src.infrastructure.serialize.pickle.load")
    @patch("src.infrastructure.serialize.open", new_callable=mock_open, read_data=b"mocked binary data")
    @patch("src.infrastructure.serialize.file_utils.file_exists", return_value=True)
    def test_deserialize_file_exists(self, mock_file_exists, mock_open_file, mock_pickle_load):
        # Arrange
        file_path = "existent_file.pkl"
        expected_data = {"key": "value"}
        mock_pickle_load.return_value = expected_data

        # Act
        result = deserialize(file_path)

        # Assert
        mock_file_exists.assert_called_once_with(file_path)
        mock_open_file.assert_called_once_with(file_path, "rb")
        mock_pickle_load.assert_called_once_with(mock_open_file())
        self.assertEqual(result, expected_data)


if __name__ == "__main__":
    unittest.main()