import re

class CSharpFileHandler:
    name = "C#"
    file_extension = ".cs"

    def is_test_file(self, file: str) -> bool:
        return "Test" in file
    
    def get_implementation_file(self, test_file: str) -> str:
        return re.sub(r'(Tests|Test)', '', test_file)