from lute.graph import Graph
from lute.node import Constant, Variable


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
