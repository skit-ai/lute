import json
import operator
from abc import ABCMeta, abstractmethod
from copy import deepcopy
from typing import Any, Dict

from lute.utils import clip_to_len


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
    """
    Metaclass for Node to ease up a few things, notably:

    1. Autogenerate Node ids for new instances.
    2. Auto call super().__init__ for direct subclass of Node. This is not
       really useful and breaks the mental model when we work with
       sub-sub-classes (where you do need to call the super().__init__
       method).
    """

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
                self.id = cls.__gen_id__()

            __init__.__wrapped__ = original_init

            cls.__init__ = __init__

        return cls


class Node(metaclass=NodeMeta):
    """
    Base class for all nodes
    """
    _count = -1

    def __init__(self, *args, **kwargs):
        self.id = None
        self._output_val = None
        self.evaluated = False
        self.predecessors = []
        self.successors = []
        self.args = []
        self.kwargs = {}

    @classmethod
    def __gen_id__(cls):
        """
        Generate a unique identifier for the node instance. This involves using the class name
        and the count of instances created.
        """

        cls._count += 1
        return "%s_%s" % (cls.__name__, cls._count)

    @property
    def value(self):
        """
        Value of the node is the `value` that the nodal computation generates. It is created by
        calling the eval function and, usually, cached.
        """

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
        """
        Register the given nodes as this node's predecessors. If a program needs to
        walk through the connections, it just need to look for the `predecessors` and
        `successors` properties of nodes.
        """

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
        """
        `id` contains sufficient information about a node so we use this directly as
        the node's string representation.
        """

        return self.id

    def __hash__(self):
        return hash(self.id)

    def __mul__(self, other):
        """
        Create a node tuple with the other node, this then can be piped to
        nodes demanding multiple input nodes.
        """

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
        """
        Overriding + operator so that basic things like list concatenation
        work nicely.
        """

        if isinstance(other, Node):
            return BinOp(operator.add)(self, other)
        else:
            raise TypeError("Unsupported right hand side")

    def name_str(self):
        """
        Unique identifier for the node (id) concatenated with the name
        given by the programmer. This is used for:

        1. Putting information in prints
        2. Resolving node by string search
        """

        if self.name is not None:
            return "{}-({})".format(self.name, self.id)
        else:
            return self.id

    def to_dict(self) -> Dict:
        """
        Dump information in a dict.
        """

        return {
            "name": self.name,
            "id": self.id,
            "evaluated": self.evaluated,
            "value": self.value if self.evaluated else None
        }

    def dumps(self) -> str:
        """
        Dump the value in json readable string.
        """

        return json.dumps(self.to_dict())

    def dumpb(self) -> bytes:
        """
        Dump to bytes. Default implementation just converts the output
        of dumps to bytes.
        """

        return bytes(self.dumps(), "utf-8")

    def __repr__(self):
        """
        Since repr shows up in repl, we put more information, including node's current
        value, in here.
        """

        return "<{}: {}>".format(self.name_str(), clip_to_len(self.dumps(), maxlen=100))


class BinOp(Node):
    """
    A binary operation node
    """

    def __init__(self, op):
        self.op = op

    def name_str(self):
        suffix = str(self.op)
        if self.name is not None:
            return "{}-({})-({})".format(self.name, suffix, self.id)
        else:
            return "{}-({})".format(suffix, self.id)

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
    """
    Node which works as a variable and used for inputting things
    in a graph.
    """

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
    """
    Node which considers a graph as a node itself. This doesn't show up
    nicely in the visualizer as of now.
    """

    def __init__(self, g):
        self.g = g

    def eval(self, *args, **kwargs):
        return self.g.run(*[a.value for a in args])
