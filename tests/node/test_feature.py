"""
Test for feature nodes
"""

from lute.graph import Graph
from lute.node import Constant, Variable
from lute.node.feature import NGrams
from lute.node.fn import fn_node


def tokenize(text: str):
    return text.split(' ')


def test_expansion():
    x = Variable()
    allowed = Constant(["world", "you"])
    g = Graph(x, ((x >> fn_node(tokenize)()) * allowed) >> NGrams())

    assert g.run("Hello world how are you") == [
        ("world",),
        ("you",),
        ("Hello", "world"),
        ("world", "how"),
        ("are", "you")
    ]
