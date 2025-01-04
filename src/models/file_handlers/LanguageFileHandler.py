from typing import List, Protocol

class LanguageFileHandler(Protocol):
    name: str
    file_extensions: List[str]

    def is_test_file(self, file: str) -> bool:
        ...

    def get_implementation_file(self, test_file: str) -> str:
        ...