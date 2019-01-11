"""
Some utitlies for nodes
"""

import types
from typing import Callable, List, Union

from lute.exceptions import ResolutionException
from lute.node import Node
from pydash import py_

NodeId = Union[str, Node]


def _resolve_filter(i: NodeId, items, fn):
    filtered = [it for it in items if fn(it)]
    if len(filtered) == 0:
        return None
    elif len(filtered) == 1:
        return filtered[0]
    else:
        raise ResolutionException(i)


def resolve(i: NodeId, nodes: List[Node]) -> Node:
    """
    Return a node with given identifier
    """

    if isinstance(i, str):
        for fn in [lambda n: n.name == i, lambda n: i in n.name_str()]:
            node = _resolve_filter(i, nodes, fn)
            if node is not None:
                return node

        raise ResolutionException(i)

    elif isinstance(i, Node):
        # Confirm if the node is in the list
        if i in nodes:
            return i
        else:
            raise ResolutionException(i)
    else:
        raise Exception("Unknown node if type")


def mute(node: Node, muting_fn: Callable = None):
    """
    Make a node work as identity transformer. If muting_fn is
    provided, it uses that to replace the evaluation method of the
    node. For example, a node with two inputs which is having this eval

    def eval(self, a, b):
        return a.value + b.value

    can be changed to always return 0 by doing:

    mute(node, lambda self, a, b: 0)
    """

    if node.fan_in == 0:
        return

    if muting_fn is None:
        if node.fan_in == 1:
            def muting_fn(self, a): return a.value
        else:
            raise RuntimeError("Cannot mute node with >1 fan-in")

    node.eval = types.MethodType(muting_fn, node)
    node.muted = True


def walk_node(node: Node, backward=False) -> List[Node]:
    """
    Walk on the node and return a list of accessible nodes
    """

    neighbours = node.predecessors if backward else node.successors
    accessible = neighbours.copy()

    for node in neighbours:
        accessible += walk_node(node, backward=backward)

    return py_.uniq(accessible)
