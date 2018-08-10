from lute.exceptions import TypeMismatchException
from lute.node import Node


class IORead(Node):
    def __init__(self, func):
        self._func = func

    def __call__(self, file_path: Node):
        self._file_path = file_path
        self._register_predecessors([file_path])

        return self

    def eval(self):
        _val = self._file_path.value
        if isinstance(_val, str):
            with open(_val, 'r') as f:
                return self._func(f)
        else:
            raise TypeMismatchException(str, type(_val))


class IOWrite(Node):
    def __init__(self, file_path: str, func):
        self._file_path = file_path
        self._func = func

    def __call__(self, data: Node):
        self._data = data
        self._register_predecessors([data])

        return self

    def eval(self):
        """
        :return: file_path if success else throws IOError
        """
        with open(self._file_path, 'w') as f:
            self._func(f, self._data.value)
            return self._file_path
