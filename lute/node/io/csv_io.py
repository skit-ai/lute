import csv
from typing import List

from .base import IORead, IOWrite


class CsvRead(IORead):

    def __init__(self):
        super().__init__()
        self._name = CsvRead.__gen_name__()

    def read_file(self, filename: str) -> List[List[str]]:
        if ".csv" not in filename:
            filename = '%s.csv' % filename

        with open(filename, newline='') as csv_file:
            reader = csv.reader(csv_file)
            return list(reader)


class CsvWrite(IOWrite):

    def __init__(self, file_path: str):
        super().__init__(file_path)
        self._name = CsvWrite.__gen_name__()

    def write_file(self, filename: str, data, delimiter=',', **kwargs):
        if ".csv" not in filename:
            filename = '%s.csv' % filename

        with open(filename, 'w') as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerows(data)

