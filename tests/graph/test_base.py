"""
Tests for graphs
"""

from lute.graph import Graph
from lute.node import Identity, Constant, Variable


def test_run():
    a = Constant("hello")
    b = Identity()(a)

    g = Graph(a, b)
    assert g.run() == "hello"


def test_run_var():
    a = Constant("hello")
    v = Variable()

    g = Graph([a, v], [a, Identity()(v)])

    assert g.run({ v: "world" }) == ["hello", "world"]
