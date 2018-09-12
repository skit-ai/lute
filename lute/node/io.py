from lute.exceptions import TypeMismatchException
from lute.node import Node


class IORead(Node):
    def __init__(self, func):
        self._func = func

    def eval(self, file_path):
        _val = file_path.value
        if isinstance(_val, str):
            with open(_val, 'r') as f:
                return self._func(f)
        else:
            raise TypeMismatchException(str, type(_val))


class IOWrite(Node):
    def __init__(self, file_path: str, func):
        self._file_path = file_path
        self._func = func

    def eval(self, data):
        """
        :return: file_path if success else throws IOError
        """
        with open(self._file_path, 'w') as f:
            self._func(f, data.value)
            return self._file_path
