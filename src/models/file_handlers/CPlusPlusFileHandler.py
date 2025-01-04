import re

class CPlusPlusFileHandler:
    name = "C++"
    file_extensions = [".cpp", ".cc", ".c++"]

    def is_test_file(self, file: str) -> bool:
        return "test" in file
    
    def get_implementation_file(self, test_file: str) -> str:
        return re.sub(r'(_test|test_)', '', test_file)