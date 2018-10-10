"""
Tests for graphs
"""

from lute.graph import Graph
from lute.node import Constant, GraphNode, Identity, Variable


def test_run():
    a = Constant("hello")
    b = Identity()(a)

    g = Graph(a, b)
    assert g.run() == "hello"


def test_input_interface():
    a = Variable()
    b = Variable()

    g = Graph([a, b], a >> Identity())

    assert g.run(1, 2) == 1
    assert g.run(values_dict={a: 1, b: 2}) == 1

    g = Graph([a], a >> Identity())
    assert g.run([1, 2]) == [1, 2]

    g = Graph(a, a >> Identity())
    assert g.run([1, 2]) == [1, 2]

    g = Graph([a, b], a + b)
    assert g.run([1, 2]) == 3


def test_run_var():
    a = Constant("hello")
    v = Variable()

    g = Graph([a, v], [a, Identity()(v)])

    assert g.run(values_dict={v: "world"}) == ["hello", "world"]


def test_graph_node():
    """
    Test if a graph node is behaving as expected
    """

    x = Variable()
    y = Constant(2)

    g = Graph(x, [x + y, y])
    gn = GraphNode(g)

    c = Constant(3)
    sg = Graph(c, gn(c))

    assert sg.run() == [5, 2]


def test_clone():
    x = Variable()
    y = Constant(2)

    g = Graph(x, [x + y, y])
    gc = g.clone()

    assert gc.run(33) == [35, 2]
    assert not x.evaluated
    assert g.run(10) == [12, 2]
    assert [n.value for n in gc.outputs] == [35, 2]
    assert [n.value for n in g.outputs] == [12, 2]
