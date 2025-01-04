import re

class CPlusPlusFileHandler:
    name = "C++"
    file_extensions = [".cpp", ".cc", ".c++"]

    def is_test_file(self, file: str) -> bool:
        return "test" in file or "Test" in file
    
    def get_implementation_file(self, test_file: str) -> str:
        remove_lowercase = re.sub(r'(_test|test_)', '', test_file)
        remove_uppercase = re.sub(r'(Tests|Test)', '', remove_lowercase)
        return remove_uppercase