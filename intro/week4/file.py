from tempfile import tempdir
import os.path

class File:
    def __init__(self, filename):
        self.filename = filename
        if not os.path.exists(filename):
            with open(filename, 'w'):
                pass
    def __str__(self):
        return self.filename
    def __iter__(self):
        self._lines_iter = iter(self.read().split('\n'))
        return self
    def __next__(self):
        line = next(self._lines_iter)
        if len(line) == 0:
            raise StopIteration
        return line + '\n'
    def read(self):
        try:
            with open(self.filename, 'r') as f:
                return f.read()
        except IOError:
            return ''
    def write(self, text):
        try:
            with open(self.filename, 'w') as f:
                return f.write(text)
        except IOError:
            return 0
    def __add__(self, other):
        splitted_names = map(lambda x: os.path.split(x)[-1], (self.filename, other.filename))
        new_filename = ''.join(splitted_names)
        new_filename = os.path.join(tempdir,new_filename)
        with open(new_filename, 'w') as f:
            f.write(self.read())
            f.write(other.read())
        return File(new_filename)
            