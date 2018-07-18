"""
Graph optimization utilities
"""

from lute.graph.graph import Graph
from lute.graph.utils import walk_node
from lute.node import Node
from pydash import py_


def prune(g: Graph) -> Graph:
    """
    Clear inputs which are not needed.
    """

    required = py_.flatten([walk_node(out, backward=True) for out in g.outputs])

    return Graph([i for i in g.inputs if i in required], outputs)
