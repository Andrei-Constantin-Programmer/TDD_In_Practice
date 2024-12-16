from typing import Protocol

class LanguageFileHandler(Protocol):
    name: str
    file_extension: str

    def is_test_file(self, file: str) -> bool:
        ...

    def get_implementation_file(self, test_file: str) -> str:
        ...