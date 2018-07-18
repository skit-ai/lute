from typing import List

from .base import IORead, IOWrite


class FileRead(IORead):

    def __init__(self):
        super().__init__()
        self._name = FileRead.__gen_name__()

    def read_file(self, filename: str) -> List[str]:
        with open(filename, 'r') as f:
            return f.read().splitlines()


class FileWrite(IOWrite):

    def __init__(self, file_path: str):
        super().__init__(file_path)
        self._name = FileWrite.__gen_name__()

    def write_file(self, filename: str, data: List[str], **kwargs):
        with open(filename, 'w') as f:
            for item in data:
                f.write(str(item) + '\n')
