import pytest

from lute.graph import Graph
from lute.node import Constant, Identity, Variable
from lute.node.fn import fn_node
from lute.node.utils import mute


def test_basic():
    x = Variable(name="input")
    a = Constant(32)
    b = Constant(1)
    c = a + b
    c.name = "stuff"

    g = Graph(x, c + x)

    sg = g.subgraph(outputs=["stuff"])

    assert g.run(2) == 35
    assert sg.run(2) == 33


def test_mute():
    a = Variable()

    def add_one(x):
        return x + 1

    b = fn_node(add_one)()(a)
    g = Graph(a, Identity()(b))

    assert g.run(3) == 4
    mute(b)
    assert g.run(3) == 3
    assert b.value == a.value


def test_mute_fail():
    a = Variable()
    b = Constant(2)

    def add(x, y):
        return x + y

    c = fn_node(add)()(a, b)
    g = Graph([a, b], c)

    assert g.run(1) == 3

    with pytest.raises(RuntimeError):
        mute(c)


def test_subgraph_input():
    x = Variable(name="x")
    c = Constant(2, name="c")

    def add(x, y):
        return x + y

    def add3(x, y, z):
        return x + y + z

    add_n = fn_node(add)
    add3_n = fn_node(add3)

    a = Identity(name="a")(x)
    b = add_n(name="b")(x, c)
    p = Identity(name="p")(a)
    q = add_n(name="q")(a, b)
    r = Identity(name="r")(b)

    y = add3_n(name="y")(p, q, r)

    g = Graph([x, c], y)

    assert g.run(1) == 8

    sg = g.clone().subgraph(["x", "c"], "y")
    assert sg.run(1) == 8

    sg = g.clone().subgraph(["a", "b"], ["y"])
    assert sg.run([11, 23]) == 68

    sg = g.clone().subgraph(["p", "q", "r"], ["y"])
    assert sg.run([1, 2, 3]) == 6
