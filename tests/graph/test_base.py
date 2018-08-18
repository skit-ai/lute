"""
Tests for graphs
"""

from lute.graph import Graph, graph_node
from lute.node import Constant, Identity, Variable


def test_run():
    a = Constant("hello")
    b = Identity()(a)

    g = Graph(a, b)
    assert g.run() == "hello"


def test_input_interface():
    a = Variable()
    b = Variable()

    g = Graph([a, b], a >> Identity())

    assert g.run([1, 2]) == 1
    assert g.run(values_dict={a: 1, b: 2}) == 1

    g = Graph([a], a >> Identity())
    assert g.run([1, 2]) == [1, 2]

    g = Graph(a, a >> Identity())
    assert g.run([1, 2]) == [1, 2]


def test_run_var():
    a = Constant("hello")
    v = Variable()

    g = Graph([a, v], [a, Identity()(v)])

    assert g.run(values_dict={ v: "world" }) == ["hello", "world"]


def test_graph_node():
    """
    Test if a graph node is behaving as expected
    """

    x = Variable()
    y = Constant(2)

    g = Graph(x, [x + y, y])
    gn = graph_node(g)

    c = Constant(3)
    sg = Graph(c, gn(c))

    assert sg.run() == [5, 2]
