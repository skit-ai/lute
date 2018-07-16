from abc import abstractmethod, ABC
from typing import Any


class Node(ABC):

    @abstractmethod
    def __init__(self):
        self.__output_val = None

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def eval(self):
        pass

    @abstractmethod
    def serialize(self):
        pass

    def clear(self):
        self.__output_val = None


class Constant(Node):
    _count = -1

    def __init__(self, value: Any):
        super().__init__()

        Constant._count += 1
        self.__name = "%s_%s" % (__class__.__name__, Constant._count)
        self.__value = value

    def name(self):
        return self.__name

    def __str__(self):
        return self.__name

    def eval(self):
        self.__output_val = self.__value
        return self.__output_val

    def serialize(self):
        pass


class Variable(Node):
    _count = -1

    def __init__(self, input: Any):
        super().__init__()
        Variable._count += 1

        self.__name = "%s_%s" % (__class__.__name__, Variable._count)

    def name(self):
        return self.__name

    def __str__(self):
        return self.__name

    def eval(self):
        pass

    def serialize(self):
        pass
