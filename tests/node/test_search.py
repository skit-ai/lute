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


def test_constraints_partial():
    constraints = [
        { "first": "moon", "second": "moon" },
        { "second": "kek" },
        { "first": "lol", "second": "kek" }
    ]

    x1 = Variable()
    x2 = Variable()
    c = ConstraintSearch(constraints, partial=True)({ "first": x1, "second": x2 })

    g = Graph([x1, x2], c)

    assert g.run({ x1: [], x2: [] }) == []
    assert g.run({ x1: [], x2: ["kek"] }) == [
        ({ "second": "kek" }, []),
        ({ "first": "lol", "second": "kek" }, ["first"])
    ]
    assert g.run({ x1: ["moon"], x2: ["moon", "kek"] }) == [
        ({ "first": "moon", "second": "moon" }, []),
        ({ "second": "kek" }, []),
        ({ "first": "lol", "second": "kek" }, ["first"])
    ]
    assert g.run({ x1: ["moon"], x2: ["kek"] }) == [
        ({ "first": "moon", "second": "moon" }, ["second"]),
        ({ "second": "kek" }, []),
        ({ "first": "lol", "second": "kek" }, ["first"])
    ]
    assert g.run({ x1: ["lol"], x2: ["kek"] }) == [
        ({ "second": "kek" }, []),
        ({ "first": "lol", "second": "kek" }, [])
    ]
    assert g.run({ x1: ["lol"], x2: ["lel"] }) == [
        ({ "first": "lol", "second": "kek" }, ["second"])
    ]


def test_constraints_complete():
    constraints = [
        { "first": "moon", "second": "moon" },
        { "second": "kek" },
        { "first": "lol", "second": "kek" }
    ]

    x1 = Variable()
    x2 = Variable()
    c = ConstraintSearch(constraints, partial=False)({ "first": x1, "second": x2 })

    g = Graph([x1, x2], c)

    assert g.run({ x1: [], x2: [] }) == []
    assert g.run({ x1: [], x2: ["kek"] }) == [
        ({ "second": "kek" }, []),
    ]
    assert g.run({ x1: ["moon"], x2: ["moon", "kek"] }) == [
        ({ "first": "moon", "second": "moon" }, []),
        ({ "second": "kek" }, [])
    ]
    assert g.run({ x1: ["moon"], x2: ["kek"] }) == [
        ({ "second": "kek" }, [])
    ]
    assert g.run({ x1: ["lol"], x2: ["kek"] }) == [
        ({ "second": "kek" }, []),
        ({ "first": "lol", "second": "kek" }, [])
    ]
    assert g.run({ x1: ["lol"], x2: ["lel"] }) == []
