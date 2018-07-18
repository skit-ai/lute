"""
Graph optimization utilities
"""

from lute.graph.graph import Graph
from lute.graph.utils import walk_node
from lute.node import Node
from pydash import py_


def prune(g: Graph) -> Graph:
    """
    Clear inputs which are not needed. Remove dangling leaf nodes.
    """

    required_inputs = [i for i in g.inputs if i in g._backward_nodes()]

    for node in g._forward_nodes():
        if node not in outputs and len(node.successors) == 0:
            for pnode in node.predecessors:
                pnode.successors.remove(node)

    return Graph(required_inputs, outputs)
