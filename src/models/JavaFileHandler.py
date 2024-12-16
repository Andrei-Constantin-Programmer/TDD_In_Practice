class JavaFileHandler:
    name = "Java"
    file_extension = ".java"

    def is_test_file(self, file: str) -> bool:
        return "Test" in file
    
    def get_implementation_file(self, test_file: str) -> str:
        return test_file.replace("Tests", "").replace("Test", "")