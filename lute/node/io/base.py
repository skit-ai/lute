from abc import abstractmethod, ABC

from lute.exceptions import TypeMismatchException
from lute.node import Node


class IORead(Node, ABC):
    def __init__(self):
        super().__init__()
        self._name = IORead.__gen_name__()

    def __call__(self, other: Node):
        super().__call__(other)
        self._file_path_node = other

        return self

    @abstractmethod
    def read_file(self, filename: str):
        ...

    def eval(self):
        _val = self._file_path_node.value
        if isinstance(_val, str):
            return self.read_file(_val)
        else:
            raise TypeMismatchException(str, type(_val))


class IOWrite(Node, ABC):
    def __init__(self, file_path: str):
        super().__init__()
        self._name = IOWrite.__gen_name__()
        self._file_path = file_path

    def __call__(self, other: Node):
        super().__call__(other)
        self._data_node = other

        return self

    @abstractmethod
    def write_file(self, filename: str, data, *args, **kwargs):
        ...

    def eval(self):
        """
        :return: file_path if success else throws IOError
        """
        self.write_file(self._file_path, self._data_node.value)
        return self._file_path
