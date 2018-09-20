import operator
import pprint
from abc import ABCMeta, abstractmethod
from copy import deepcopy
from typing import Any

pp = pprint.PrettyPrinter(indent=2, width=50)


class NodeTuple:
    """
    A collection type for working with parallel piping
    """

    def __init__(self, nodes=None):
        if nodes is None:
            nodes = []
        self.nodes = nodes

    def __getitem__(self, key):
        return self.nodes[key]

    def __mul__(self, other_node):
        self.nodes.append(other_node)
        return self

    def __rshift__(self, other):
        if isinstance(other, Node):
            return other(*self.nodes)
        elif isinstance(other, NodeTuple):
            return NodeTuple([o(*self.nodes) for o in other])
        else:
            raise TypeError("Unknown right hand side encountered while piping")


class NodeMeta(ABCMeta):
    def __new__(meta_cls, *args, **kwargs):
        cls = super().__new__(meta_cls, *args, **kwargs)

        base_cls = "Node"
        if cls.__name__ != base_cls:
            original_init = cls.__init__

            def __init__(self, *args, name=None, **kwargs):
                if base_cls in [c.__name__ for c in cls.__bases__]:
                    # Only auto call super for the direct children of base_cls
                    super(cls, self).__init__(*args, **kwargs)

                original_init(self, *args, **kwargs)
                self.name = name
                self._id = cls.__gen_id__()

            __init__.__wrapped__ = original_init

            cls.__init__ = __init__

        return cls


class Node(metaclass=NodeMeta):
    """
    Base class for all nodes
    """
    _count = -1

    def __init__(self, *args, **kwargs):
        self._id = None
        self._output_val = None
        self.evaluated = False
        self.predecessors = []
        self.successors = []
        self.args = []
        self.kwargs = {}

    @classmethod
    def __gen_id__(cls):
        cls._count += 1
        return "%s_%s" % (cls.__name__, cls._count)

    @property
    def value(self):
        if not self.evaluated:
            self._output_val = self.eval(*self.args, **self.kwargs)
            self.evaluated = True

        return self._output_val

    @abstractmethod
    def eval(self, *args, **kwargs):
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
        if self.evaluated:
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

    @property
    def fan_in(self):
        return len(self.predecessors)

    @property
    def fan_out(self):
        return len(self.successors)

    def __call__(self, *args, **kwargs):
        """
        Default implementation of call, assumes nodes everywhere
        """
        inputs = list(args) + list(kwargs.values())
        self._register_predecessors([ip for ip in inputs if isinstance(ip, Node)])
        self.args = args
        self.kwargs = kwargs

        return self

    def clone(self):
        return deepcopy(self)

    def __str__(self):
        return self._id

    def __hash__(self):
        return hash(self._id)

    def __mul__(self, other):
        if isinstance(other, Node):
            return NodeTuple([self, other])
        else:
            raise TypeError("Unknown right hand side while making NodeTuple")

    def __rshift__(self, other):
        """
        Overriding >> for piping
        """

        if isinstance(other, Node):
            return other(self)
        elif isinstance(other, NodeTuple):
            return NodeTuple([o(self) for o in other])
        else:
            raise TypeError("Unknown right hand side encountered while piping")

    def __add__(self, other):
        if isinstance(other, Node):
            return BinOp(operator.add)(self, other)
        else:
            raise TypeError("Unsupported right hand side")

    def name_str(self):
        if self.name is not None:
            return "{}-({})".format(self.name, self._id)
        else:
            return self._id

    def value_str(self, pretty=False):
        if self.evaluated:
            if pretty:
                return pp.pformat(self.value)
            else:
                return repr(self.value)
        else:
            return "unevaluated"

    def __repr__(self):
        return "<{}: {}>".format(self.name_str(), self.value_str())


class BinOp(Node):
    """
    A binary operation node
    """

    def __init__(self, op):
        self.op = op

    def name_str(self):
        suffix = str(self.op)
        if self.name is not None:
            return "{}-({})-({})".format(self.name, suffix, self._id)
        else:
            return "{}-({})".format(suffix, self._id)

    def eval(self, a: Node, b: Node):
        return self.op(a.value, b.value)


class Constant(Node):
    """
    Node with constant value. Will always cache the value, even after
    clear() is called
    """

    def __init__(self, value: Any):
        self._value = value

    def eval(self):
        return self._value

    def __call__(self, *args, **kwargs):
        raise Exception("uncallable node")


class Variable(Node):

    def eval(self):
        return self._output_val

    def __call__(self, *args, **kwargs):
        raise Exception("uncallable node")

    @Node.value.setter
    def value(self, val):
        self._output_val = val


class Identity(Node):
    """
    Passes on the value of input
    """

    def eval(self, _input):
        return _input.value


class GraphNode(Node):

    def __init__(self, g):
        self.g = g

    def eval(self, *args, **kwargs):
        return self.g.run(*[a.value for a in args])
