from abc import ABCMeta, abstractmethod
from typing import Any


class NodeMeta(ABCMeta):
    def __new__(meta_cls, *args, **kwargs):
        cls = super().__new__(meta_cls, *args, **kwargs)

        base_cls = "Node"
        if cls.__name__ != base_cls:
            original_init = cls.__init__
            def __init__(self, *args, **kwargs):
                if base_cls in [c.__name__ for c in cls.__bases__]:
                    # Only auto call super for the direct children of base_cls
                    super(cls, self).__init__(*args, **kwargs)
                self._id = cls.__gen_id__()
                original_init(self, *args, **kwargs)
            cls.__init__ = __init__

        return cls


class Node(metaclass=NodeMeta):
    """
    Base class for all nodes
    """
    _count = -1

    @abstractmethod
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get("name")
        self._id = None
        self._output_val = None
        self.evaluated = False
        self.predecessors = []
        self.successors = []

    @classmethod
    def __gen_id__(cls):
        cls._count += 1
        return "%s_%s" % (cls.__name__, cls._count)

    @property
    def value(self):
        if not self.evaluated:
            self._output_val = self.eval()
            self.evaluated = True

        return self._output_val

    @abstractmethod
    def eval(self):
        """
        Perform actual evaluation steps for the node
        and return the output
        """

        ...

    def clear(self):
        """
        clears the cached input of the node
        """

        # Guarding against cyclic traps
        if self.evaluated == True:
            self.evaluated = False

            # Free some memory too
            self._output_val = None

            # Free up all successors too
            for succ in self.successors:
                succ.clear()

    def _register_predecessors(self, predecessors):
        self.predecessors = predecessors
        for pred in predecessors:
            if self not in pred.successors:
                pred.successors.append(self)

    def __str__(self):
        return self._id

    def __eq__(self, other):
        return other._id == self._id

    def __hash__(self):
        return hash(self._id)

    def __repr__(self):
        name_str = self._id
        if self.name is not None:
            name_str = "{}-({})".format(self.name, name_str)

        value_str = repr(self.value) if self.evaluated else "unevaluated"

        return "<{}: {}>".format(name_str, value_str)


class Constant(Node):
    """
    Node with constant value. Will always cache the value, even after
    clear() is called
    """

    def __init__(self, value: Any):
        self._value = value

    def eval(self):
        return self._value

    def __call__(self, other: Node):
        raise Exception("uncallable node")


class Variable(Node):

    def __init__(self):
        pass

    def eval(self):
        return self._output_val

    def __call__(self, other: Node):
        raise Exception("uncallable node")

    @Node.value.setter
    def value(self, val):
        self._output_val = val


class Identity(Node):
    """
    Passes on the value of input
    """

    def __init__(self):
        pass

    def eval(self):
        return self._source_node.value

    def __call__(self, other: Node):
        self._register_predecessors([other])
        self._source_node = other

        return self
