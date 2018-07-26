"""
Test for feature nodes
"""

from lute.graph import Graph
from lute.node import Constant, Variable
from lute.node.feature.base import NGrams
from lute.node.preprocess import Tokenizer


def test_expansion():
    x = Variable()
    allowed = Constant(["world", "you"])
    g = Graph(x, ((x >> Tokenizer("en")) * allowed) >> NGrams())

    assert g.run("Hello world how are you") == [
        ("world",),
        ("you",),
        ("Hello", "world"),
        ("world", "how"),
        ("are", "you")
    ]
