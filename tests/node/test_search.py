from lute.graph import Graph
from lute.node import Constant, Identity, Variable
from lute.node.search import ExpansionSearch, ListSearch
from lute.node.search.constraint import ConstraintSearch


def test_expansion():
    exp = {
        "hello": ["hola", "hello", "hey"],
        "world": ["planet earth", "world", "universe"]
    }

    x = Variable()
    e = ExpansionSearch(["hello", "world"], exp)(x)
    g = Graph(x, e)

    assert g.run({ x: "Hello world" }) == ["hello", "world"]
    assert g.run({ x: "hola planet earth" }) == ["hello", "world"]
    assert g.run({ x: "hola planet mars" }) == ["hello"]
    assert g.run({ x: "lol planet mars" }) == []


def test_list():
    terms = [
        "Blue moon",
        "venus",
        "divider"
    ]

    x = Variable()
    e = ListSearch(terms)(x)
    g = Graph(x, e)

    assert g.run({ x: "Hello world" }) == []
    assert g.run({ x: "hola planet venus" }) == ["venus"]
    assert g.run({ x: "What is a blue moon?" }) == ["Blue moon"]


def test_constraints():
    constraints = [["moon", "moon"], [None, "kek"], [None, None], ["lol", "lel"]]

    x1 = Variable()
    x2 = Variable()
    c = ConstraintSearch(constraints)([x1, x2])

    g = Graph([x1, x2], c)

    assert g.run({ x1: [], x2: [] }) == []
    assert g.run({ x1: ["moon"], x2: [] }) == []
    assert g.run({ x1: ["moon"], x2: ["moon", "kek"] }) == [["moon", "moon"], [None, "kek"]]
    assert g.run({ x1: ["moon"], x2: ["kek"] }) == [[None, "kek"]]
    assert g.run({ x1: ["lol"], x2: ["kek"] }) == [[None, "kek"]]
    assert g.run({ x1: ["lol"], x2: ["lel"] }) == [["lol", "lel"]]
