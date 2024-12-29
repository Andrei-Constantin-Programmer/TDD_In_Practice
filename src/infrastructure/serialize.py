import pickle
from typing import Any
from src.infrastructure import file_utils

def serialize(file_path: str, data: Any):
    '''
    Serializes the given data and stores it in a file.
    @param file_path: The file where the serialized data is stored to.
    @param data: The data to serialize.
    '''
    with open(file_path, "wb") as file:
        pickle.dump(data, file)

def deserialize(file_path: str):
    '''
    Deserializes the data at the given file path.
    @param file_path: The file where the serialized data is stored to.
    @return: The deserialized data, or None if the file does not exist.
    '''
    if not file_utils.file_exists(file_path):
        raise FileNotFoundError(f"Serialized file not found at {file_path}.")
    
    with open(file_path, "rb") as file:
        return pickle.load(file)
