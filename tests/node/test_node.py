from lute.graph import Graph
from lute.node import Constant, Identity, Variable
from lute.node.fn import fn_node, node_fn
from lute.node.search import ListSearch


def test_id():
    Constant._count = -1
    Variable._count = -1

    c = Constant(2)
    assert c._id == 'Constant_0'

    c1 = Constant(3)
    assert c1._id == 'Constant_1'

    v = Variable()
    assert v._id == 'Variable_0'

    v1 = Variable()
    assert v1._id == 'Variable_1'


def test_names():
    c = Constant(3, name="rerer")
    assert c.name == "rerer"

    ls = ListSearch([], name="rerer")
    assert ls.name == "rerer"


def what_func(a, b, c):
    a = b + c
    return a


def which_func(a):
    a = a + 1
    return a


def some_add_func(a, b):
    return (a + 1, b + 1)


def what_what_func(a, b, c):
    a, b = some_add_func(a, b)
    return (a, b, c)


def test_multiple_assignments():
    x = Variable()
    y = Variable()
    z = Variable()
    func_node = fn_node(what_what_func)()(x, y, z)
    g = Graph([x, y, z], func_node)
    a, b, c = g.run(values_dict={
        x: 1,
        y: 2,
        z: 3
    })
    assert a == 2
    assert b == 3
    assert c == 3


def conditional_func(a, b):
    if True:
        a = a + 1
    else:
        b = b + 1
    return 22


def test_conditional_call():
    """
    Test if the calls to function is evaluating branches which
    shouldn't get evaluated.
    """

    a = Variable()
    b = Variable()

    # Set values for a only
    a.value = 22

    N = fn_node(conditional_func)()
    N(a, b)

    # Don't set anything here
    # Since branch for b won't run, updation of b should not throw error
    assert N.value == 22


def test_func_node_replacement():
    x = Constant(2)
    g = Graph(x, x >> fn_node(which_func)())
    assert g.run() == 3


def test_something():
    x = Variable()

    y = x >> fn_node(which_func)()
    z = x >> fn_node(which_func)()
    g = Graph(x, [y, z])
    y_out, z_out = g.run(10)
    assert y_out == z_out


def test_func_node():
    x = Variable()
    y = Variable()
    z = Variable()
    func_node = fn_node(what_func)()(x, y, z)
    g = Graph([x, y, z], func_node)
    result = g.run(values_dict={
        x: 1,
        y: 2,
        z: 3
    })
    assert (result == 5)


def tokenize(test: str):
    return test.split(' ')


def test_node_func_interface():
    s = "hello world"
    tk_s = ["hello", "world"]

    assert node_fn(Identity)(s) == s
    assert node_fn(Identity())(s) == s
    assert node_fn()(Identity())(s) == s
    assert node_fn()(Identity)(s) == s

    assert node_fn("en")(fn_node(tokenize)())(s) == tk_s
    # The instance arguments takes precedence here
    assert node_fn("en")(fn_node(tokenize)())(s) == tk_s
    assert node_fn(fn_node(tokenize)())(s) == tk_s


def test_fn_node_lambda():
    try:
        fn_node(lambda x: x + 1)
        assert False
    except Exception:
        assert True

    try:
        a = lambda x: x
        fn_node(a)
        assert False
    except Exception:
        assert True


def fn_conditional(x, y):
    if y > 1:
        x = x + 1
    x = x + 2
    return x


def test_fn_conditional():
    assert fn_node(fn_conditional)()(Constant(1), Constant(1)).value == 3
    assert fn_node(fn_conditional)()(Constant(1), Constant(3)).value == 4


def test_fn_indent():
    def lol(x):
        return x + 1

    assert fn_node(lol)()(Constant(1)).value == 2


def test_add():
    n = Constant(34) + Constant(3)
    assert n.value == 37
    assert (Constant([1, 2, 3]) + Constant([4])).value == [1, 2, 3, 4]


def test_iadd():
    n = Constant(2)
    n += Constant(20)
    assert n.value == 22
