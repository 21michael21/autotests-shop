class FileWriter:
    def __init__(self,filename:str):
        self.filename = filename


    def __enter__(self):
        self.file = open(self.filename, 'w')
        return self.file
    
    def __exit__(self, type, value, traceback):
        self.file.close()


with FileWriter('example.txt') as file:
    file.write("Hello, World!")
