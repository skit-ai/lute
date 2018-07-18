import json
from typing import Dict

from .base import IORead, IOWrite


class JSONRead(IORead):
    def __init__(self):
        super().__init__()
        self._name = JSONRead.__gen_name__()

    def read_file(self, filename: str) -> Dict:
        if ".json" not in filename:
            filename = '%s.json' % filename

        with open(filename) as json_file:
            return json.load(json_file)


class JSONWrite(IOWrite):
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self._name = JSONWrite.__gen_name__()

    def write_file(self, filename: str, data: Dict, encoding='utf-8', *args, **kwargs):
        if ".json" not in filename:
            filename = '%s.json' % filename

        with open(filename, 'w', encoding=encoding) as json_file:
            json.dump(data, json_file, ensure_ascii=False)
