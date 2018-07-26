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

    assert g.run("Hello world") == [{
        "type": "expansion",
        "value": "hello",
        "range": (0, 5)
    }, {
        "type": "expansion",
        "value": "world",
        "range": (6, 11)
    }]
    assert g.run("hola planet earth") == [{
        "type": "expansion",
        "value": "hello",
        "range": (0, 4)
    }, {
        "type": "expansion",
        "value": "world",
        "range": (5, 17)
    }]
    assert g.run("hola planet mars") == [{
        "type": "expansion",
        "value": "hello",
        "range": (0, 4)
    }]
    assert g.run("lol planet mars") == []


def test_expansion_hi():
    exp = {
        "account": ["सैलरी अकाउंट", "सेविंग्स अकाउंट"],
        "card": ["कार्ड", "कॉर्ड"],
        "lost": ["खो", "गुम", "गायब", "लुप्त"]
    }

    x = Variable()
    g = Graph(x, x >> ExpansionSearch(["account", "card", "lost"], exp, lang="hi"))

    assert g.run("कार्ड खो गया है") == [{
        "type": "expansion",
        "value": "card",
        "range": (0, 5)
    }, {
        "type": "expansion",
        "value": "lost",
        "range": (6, 8)
    }]
    assert g.run("सैलरी अकाउंट चाहिए") == [{
        "type": "expansion",
        "value": "account",
        "range": (0, 12)
    }]


def test_list():
    terms = [
        "Blue moon",
        "venus",
        "divider"
    ]

    x = Variable()
    e = ListSearch(terms)(x)
    g = Graph(x, e)

    assert g.run("Hello world") == []
    assert g.run("hola planet venus") == [{ "type": "list", "value": "venus", "range": (12, 17) }]
    assert g.run("What is a blue moon?") == [{ "type": "list", "value": "Blue moon", "range": (10, 19) }]


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

    assert g.run(values_dict={ x1: [], x2: [] }) == []
    assert g.run(values_dict={ x1: [], x2: ["kek"] }) == [
        ({ "second": "kek" }, []),
        ({ "first": "lol", "second": "kek" }, ["first"])
    ]
    assert g.run(values_dict={ x1: ["moon"], x2: ["moon", "kek"] }) == [
        ({ "first": "moon", "second": "moon" }, []),
        ({ "second": "kek" }, []),
        ({ "first": "lol", "second": "kek" }, ["first"])
    ]
    assert g.run(values_dict={ x1: ["moon"], x2: ["kek"] }) == [
        ({ "first": "moon", "second": "moon" }, ["second"]),
        ({ "second": "kek" }, []),
        ({ "first": "lol", "second": "kek" }, ["first"])
    ]
    assert g.run(values_dict={ x1: ["lol"], x2: ["kek"] }) == [
        ({ "second": "kek" }, []),
        ({ "first": "lol", "second": "kek" }, [])
    ]
    assert g.run(values_dict={ x1: ["lol"], x2: ["lel"] }) == [
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

    assert g.run(values_dict={ x1: [], x2: [] }) == []
    assert g.run(values_dict={ x1: [], x2: ["kek"] }) == [
        ({ "second": "kek" }, []),
    ]
    assert g.run(values_dict={ x1: ["moon"], x2: ["moon", "kek"] }) == [
        ({ "first": "moon", "second": "moon" }, []),
        ({ "second": "kek" }, [])
    ]
    assert g.run(values_dict={ x1: ["moon"], x2: ["kek"] }) == [
        ({ "second": "kek" }, [])
    ]
    assert g.run(values_dict={ x1: ["lol"], x2: ["kek"] }) == [
        ({ "second": "kek" }, []),
        ({ "first": "lol", "second": "kek" }, [])
    ]
    assert g.run(values_dict={ x1: ["lol"], x2: ["lel"] }) == []
