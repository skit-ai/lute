"""
Graph optimization utilities
"""

from lute.graph.graph import Graph
from lute.node import Node
from pydash import py_


def prune(g: Graph) -> Graph:
    """
    Clear inputs which are not needed.
    """

    def _walk_back(n: Node):
        pred = n.predecessors
        back_nodes = pred.copy()
        for p in pred:
            back_nodes += _walk_back(p)
        return back_nodes

    needed = py_.flatten([_walk_back(out) for out in g.outputs])

    return Graph([i for i in g.inputs if i in needed], outputs)
