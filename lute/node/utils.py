"""
Some utitlies for nodes
"""

from typing import List, Union

from pydash import py_

from lute.exceptions import ResolutionException
from lute.node import Node

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


def mute(node: Node):
    """
    Make a node work as identity transformer
    """

    if len(node.predecessors) == 0:
        return
    elif len(node.predecessors) == 1:
        node.eval = lambda: node.predecessors[0].value
        node.muted = True
    if len(node.predecessors) > 1:
        raise RuntimeError("Cannot mute node with >1 fan-in")


def walk_node(node: Node, backward=False) -> List[Node]:
    """
    Walk on the node and return a list of accessible nodes
    """

    neighbours = node.predecessors if backward else node.successors
    accessible = neighbours.copy()

    for node in neighbours:
        accessible += walk_node(node, backward=backward)

    return py_.uniq(accessible)
