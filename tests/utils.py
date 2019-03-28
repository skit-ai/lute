from lute.graph import Graph
from lute.node import Constant, Identity, Variable


def make_test_graph() -> Graph:
    """
    Make a graph with major features present
    """

    x = Variable()
    y = Variable()

    z = x + y

    c1 = Constant([{
        "something": "this is a long text"
    }] * 100)

    return Graph([x, y], [Identity()(c1), z])
