# Class for reading text file
# 
import sys
class FileReader():
    
    def __init__(self, filename=''):
        self.filename = filename
        self._file_str = ''
        self._read()
    file_str = property()

    @file_str.setter
    def file_str(self, value):
        if isinstance(value, str):
            self._file_str = value
    @file_str.getter
    def file_str(self):
        return self._file_str

    def _read(self):
        try:
            with open(self.filename, 'r') as f:
                self.file_str = f.read()
        except IOError:
            pass
    def read(self):
        return self.file_str

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Specify file to read")
        exit()
    filename = sys.argv[1]
    filereader = FileReader(filename)
    print(filereader.read())
