from collections import UserDict
import os.path


class IndexContext(UserDict):
    def __init__(self, path):
        initial = {
            'basename': self.basename(path),
            'path': path,
        }
        super().__init__(initial)

    @staticmethod
    def basename(path):
        if path.endswith('/'):
            path = path[:-1]
        return os.path.basename(path)
