"""
Test for feature nodes
"""

from lute.graph import Graph
from lute.node import Constant, Variable
from lute.node.feature import NGrams, POSTagger
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


def test_pos_tagger():
    _text = Variable()

    _url = "http://localhost:8002/api/v1/namespaces/default/services/syntaxnet/proxy/"
    _lang = "hi"

    g = Graph(_text, _text >> POSTagger(_url, _lang))

    out = g.run("मुझे खाना दो")

    assert out[0]['xpostag'] == 'PRP'
    assert out[1]['xpostag'] == 'NN'
    assert out[2]['xpostag'] == 'QC'
