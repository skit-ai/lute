"""
Test piping features
"""

from lute.node import Constant, Identity, Node
from lute.node.fn import fn_node


def square(x):
    return x ** 2


def bin_add(x, y):
    return x + y


def test_linear():
    c = Constant(22)
    res = c >> Identity() >> fn_node(square)()
    assert res.value == 484


def test_diamond():
    c = Constant(22)
    res = c >> Identity() * fn_node(square)() >> fn_node(bin_add)()
    assert res.value == 506


def test_right_arrow():
    res = Constant(10) * Constant(30) >> fn_node(bin_add)()
    assert res.value == 40


def test_quad():
    c = Constant(22)
    res = c >> Identity() * Identity() >> fn_node(bin_add)() * fn_node(bin_add)() >> fn_node(bin_add)()
    assert res.value == 88


def test_unpack():
    c = Constant(22)
    a, b = c >> Identity() * fn_node(square)()

    assert a.value == 22
    assert b.value == 484
