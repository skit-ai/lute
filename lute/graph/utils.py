"""
Some utilities for working with graphs
"""

from typing import List, Union

from lute.exceptions import ResolutionException
from lute.node import Node

NodeId = Union[str, Node]


def _resolve_filter(i: NodeId, items, fn):
    filtered = [it for it in items if fn(it)]
    if len(filtered) == 0:
        return None
    elif len(filtered) == 1:
        return filtered[1]
    else:
        raise ResolutionException(i)


def resolve(i: NodeId, nodes: List[Node]) -> Node:
    """
    Return a node with given identifier
    """

    if isinstance(i, str):
        for fn in [lambda n: n.name == i, lambda n: n.name_str().startswith(i)]:
            node = _resolve_filter(i, nodes, fn)
            if node is not None:
                return node

        return ResolutionException(i)

    elif isinstance(i, Node):
        # Confirm if the node is in the list
        if i in nodes:
            return i
        else:
            raise ResolutionException(i)
    else:
        raise Exception("Unknown node if type")
