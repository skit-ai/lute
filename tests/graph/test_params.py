"""
Tests for working with parameters
"""

from lute.graph import Graph
from lute.node import Constant, Node


class TunaNode(Node):
    """
    A simple node with tunable param
    """

    def __init__(self, alpha=10):
        self.alpha = alpha

    def __call__(self, other: Node):
        self._register_predecessors([other])

        self.other = other
        return self

    def eval(self):
        return self.other.value + self.alpha


def test_set():
    c = Constant(23)
    tn = c >> TunaNode(10)

    g = Graph(c, c >> tn)
    assert g.run() == 33

    g.set_param((tn, "alpha"), 40)
    assert tn.alpha == 40


def test_resolution():
    c = Constant(23)
    tn = c >> TunaNode(10)

    g = Graph(c, c >> tn)
    assert g.run() == 33

    g.set_param("alpha", 40)
    assert tn.alpha == 40
