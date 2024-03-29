"""
Graph optimization utilities
"""

from lute.graph.base import Graph
from lute.node.utils import walk_node
from lute.node import Node
from pydash import py_


def prune(g: Graph) -> Graph:
    """
    Clear inputs which are not needed. Remove dangling leaf nodes.
    Mutates the involved nodes when removing danglers.
    """

    required_inputs = [i for i in g.inputs if i in g._backward_nodes()]

    for node in g._forward_nodes():
        if node not in g.outputs and len(node.successors) == 0:
            for pnode in node.predecessors:
                pnode.successors.remove(node)

    return Graph(required_inputs, g.outputs)
