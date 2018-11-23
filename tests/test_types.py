"""
Test for types in nodes and graphs
"""

from lute.graph import Graph
from lute.node import Constant, GraphNode, Identity, Node, Variable


class KekNode(Node):
    def eval(self):
        return 34


def test_basic():
    n = Constant("lole")
    assert n.type == str


def test_setting():
    n = KekNode(type=int)
    assert n.type == int


def test_prop():
    n = KekNode(type=int)
    c = Constant(343)

    out = c + n
    assert out.type == int


def test_graph():
    v = Variable(type=list)
    g = Graph(v, v + v)

    assert g.type == [list]

    gn = GraphNode(g)

    assert gn.type == g.type
