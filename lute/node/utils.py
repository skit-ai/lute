"""
Some utitlies for nodes
"""

from typing import List

from pydash import py_

from lute.node.base import Node


def walk_node(node: Node, backward=False) -> List[Node]:
    """
    Walk on the node and return a list of accessible nodes
    """

    neighbours = node.predecessors if backward else node.successors
    accessible = neighbours.copy()

    for node in neighbours:
        accessible += walk_node(node)

    return py_.uniq(accessible)
