import pytest
from lute.graph import Graph
from lute.node import Variable
from lute.node.fn import node_fn
from lute.node.search.constraint import ConstraintSearch
from lute.node.search.generic import Canonicalize, ExpansionSearch, ListSearch


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


def test_expansion_regex():
    exp = {
        "hello": ["hola", "hell?o", "hey!?( there)?"],
        "world": ["planet( earth| venus| kek)+", "world", "universe"]
    }

    x = Variable()
    e = ExpansionSearch(["hello", "world"], exp)(x)
    g = Graph(x, e)

    assert g.run("Helo world") == [{
        "type": "expansion",
        "value": "hello",
        "range": (0, 4)
    }, {
        "type": "expansion",
        "value": "world",
        "range": (5, 10)
    }]
    assert g.run("hey there, thank you!") == [{
        "type": "expansion",
        "value": "hello",
        "range": (0, 9)
    }]
    assert g.run("hola planet") == [{
        "type": "expansion",
        "value": "hello",
        "range": (0, 4)
    }]
    assert g.run("hola planet mars") == [{
        "type": "expansion",
        "value": "hello",
        "range": (0, 4)
    }]
    assert g.run("lol planet kek") == [{
        "type": "expansion",
        "value": "world",
        "range": (4, 14)
    }]


def test_expansion_regex_hi():
    exp = {
        "account": ["(सैलरी |सेविंग्स )?अकाउंट"],
        "card": ["कार्ड", "कॉर्ड"],
        "lost": ["खो(या|ये|ए)?", "गु(म|मा)", "गायब", "लुप्त"]
    }

    x = Variable()
    g = Graph(x, x >> ExpansionSearch(["account", "card", "lost"], exp, lang="hi"))

    assert g.run("कार्ड खोया था") == [{
        "type": "expansion",
        "value": "card",
        "range": (0, 5)
    }, {
        "type": "expansion",
        "value": "lost",
        "range": (6, 10)
    }]
    assert g.run("सैलरी अकाउंट चाहिए") == [{
        "type": "expansion",
        "value": "account",
        "range": (0, 12)
    }]
    assert g.run("अकाउंट चाहिए") == [{
        "type": "expansion",
        "value": "account",
        "range": (0, 6)
    }]


def test_canonicalization():
    exp = {
        "hello": ["hola", "hello", "hey"],
        "world": ["earth", "planet earth", "world", "universe"]
    }

    terms = ["hello", "world"]

    x = Variable()
    c = Canonicalize()(x, x >> ExpansionSearch(terms, exp))
    g = Graph(x, c)

    assert g.run("hola universe") == "hello world"
    assert g.run("hey planet earth") == "hello world"


def test_canonicalization_dup():
    exp = {
        "hello": ["hola", "hello", "hey"],
        "world": ["earth", "planet earth", "world", "universe"]
    }

    terms = ["hello", "world"]

    x = Variable()
    es = ExpansionSearch(terms, exp)(x)

    c_dup = Canonicalize(remove_duplicates=False)(x, es)
    g_dup = Graph(x, c_dup)

    c = Canonicalize(remove_duplicates=True)(x, es)
    g = Graph(x, c)

    assert g_dup.run("hey planet earth universe world") == "hello world world world"
    assert g.run("hey planet earth universe world") == "hello world"


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
    assert g.run("hola planet venus") == [{"type": "list", "value": "venus", "range": (12, 17)}]
    assert g.run("What is a blue moon?") == [{"type": "list", "value": "Blue moon", "range": (10, 19)}]


def test_list_regex():
    terms = [
        "Hello - world",
        "f*ck"
    ]

    fn = node_fn(ListSearch(terms))

    assert fn("Hello world, how art thou?") == []
    assert fn("Hello - world, how art thou?") == [{"type": "list", "value": terms[0], "range": (0, 13)}]
    assert fn("what the f*ck!") == [{"type": "list", "value": terms[1], "range": (9, 13)}]


def test_constraints_partial():
    constraints = [
        {"name": "1", "items": {"first": "moon", "second": "moon"}},
        {"name": "2", "items": {"second": "kek"}},
        {"name": "3", "items": {"first": "lol", "second": "kek"}}
    ]

    x1 = Variable()
    x2 = Variable()
    c = ConstraintSearch(constraints, partial=True)({"first": x1, "second": x2})

    g = Graph([x1, x2], c)

    assert g.run(values_dict={x1: [], x2: []}) == []
    assert g.run(values_dict={x1: [], x2: [{"type": "search_type", "value": "kek"}]}) == [
        {"type": "constraint", "name": "2", "constraint": {"second": "kek"}, "missing": [], "score": 1.0},
        {"type": "constraint", "name": "3", "constraint": {"first": "lol", "second": "kek"}, "missing": ["first"], "score": 0.5}
    ]
    assert g.run(values_dict={x1: [{"type": "search_type", "value": "moon"}],
                              x2: [{"type": "search_type", "value": "moon"},
                                   {"type": "search_type", "value": "kek"}]}) == [
               {"type": "constraint", "name": "1", "constraint": {"first": "moon", "second": "moon"}, "missing": [], "score": 1.0},
               {"type": "constraint", "name": "2", "constraint": {"second": "kek"}, "missing": [], "score": 1.0},
               {"type": "constraint", "name": "3", "constraint": {"first": "lol", "second": "kek"}, "missing": ["first"], "score": 0.5}
           ]
    assert g.run(values_dict={x1: [{"type": "search_type", "value": "moon"}],
                              x2: [{"type": "search_type", "value": "kek"}]}) == [
               {"type": "constraint", "name": "2", "constraint": {"second": "kek"}, "missing": [], "score": 1.0},
               {"type": "constraint", "name": "1", "constraint": {"first": "moon", "second": "moon"}, "missing": ["second"], "score": 0.5},
               {"type": "constraint", "name": "3", "constraint": {"first": "lol", "second": "kek"}, "missing": ["first"], "score": 0.5}
           ]
    assert g.run(values_dict={x1: [{"type": "search_type", "value": "lol"}],
                              x2: [{"type": "search_type", "value": "kek"}]}) == [
               {"type": "constraint", "name": "2", "constraint": {"second": "kek"}, "missing": [], "score": 1.0},
               {"type": "constraint", "name": "3", "constraint": {"first": "lol", "second": "kek"}, "missing": [], "score": 1.0}
           ]
    assert g.run(values_dict={x1: [{"type": "search_type", "value": "lol"}],
                              x2: [{"type": "search_type", "value": "lel"}]}) == [
               {"type": "constraint", "name": "3", "constraint": {"first": "lol", "second": "kek"}, "missing": ["second"], "score": 0.5}
           ]


def test_constraints_complete():
    constraints = [
        {"name": "1", "items": {"first": "moon", "second": "moon"}},
        {"name": "2", "items": {"second": "kek"}},
        {"name": "3", "items": {"first": "lol", "second": "kek"}}
    ]

    x1 = Variable()
    x2 = Variable()
    c = ConstraintSearch(constraints, partial=False)({"first": x1, "second": x2})

    g = Graph([x1, x2], c)

    assert g.run(values_dict={x1: [], x2: []}) == []
    assert g.run(values_dict={x1: [], x2: [{"type": "search_type", "value": "kek"}]}) == [
        {"type": "constraint", "name": "2", "constraint": {"second": "kek"}, "missing": [], "score": 1.0},
    ]
    assert g.run(values_dict={x1: [{"type": "search_type", "value": "moon"}],
                              x2: [{"type": "search_type", "value": "moon"},
                                   {"type": "search_type", "value": "kek"}]}) == [
               {"type": "constraint", "name": "1", "constraint": {"first": "moon", "second": "moon"}, "missing": [], "score": 1.0},
               {"type": "constraint", "name": "2", "constraint": {"second": "kek"}, "missing": [], "score": 1.0}
           ]
    assert g.run(values_dict={x1: [{"type": "search_type", "value": "moon"}],
                              x2: [{"type": "search_type", "value": "kek"}]}) == [
               {"type": "constraint", "name": "2", "constraint": {"second": "kek"}, "missing": [], "score": 1.0}
           ]
    assert g.run(values_dict={x1: [{"type": "search_type", "value": "lol"}],
                              x2: [{"type": "search_type", "value": "kek"}]}) == [
               {"type": "constraint", "name": "2", "constraint": {"second": "kek"}, "missing": [], "score": 1.0},
               {"type": "constraint", "name": "3", "constraint": {"first": "lol", "second": "kek"}, "missing": [], "score": 1.0}
           ]
    assert g.run(values_dict={x1: [{"type": "search_type", "value": "lol"}],
                              x2: [{"type": "search_type", "value": "lel"}]}) == []
