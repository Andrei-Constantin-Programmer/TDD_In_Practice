class CustomCommit:
    def __init__(self, hash, modified_files, author, date):
        self.hash = hash
        self.modified_files = modified_files
        self.author = author
        self.date = date
        self.size = len(self.modified_files)

    def __str__(self):
        return ("\nCOMMIT - " + self.hash +
                "\nMODIFIED - " + str(self.modified_files) +
                "\nAUTHOR - " + str(self.author) +
                "\nDATE - " + str(self.date) + "\n" +
                "\nSIZE - " + str(self.size))