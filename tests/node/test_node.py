from lute.graph import Graph
from lute.node import Constant, Variable
from lute.node.fn import fn_node


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

def what_func(a, b, c):
    a = b+c
    return a

def which_func(a):
    a = a + 1
    return a

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

    g = Graph([a, b], N(a, b))

    # Don't set anything here
    # Since branch for b won't run, updation of b should not throw error
    assert g.run() == 22

def test_func_node_replacement():
    x = Constant(2)
    g = Graph(x, x >> fn_node(which_func)())
    assert g.run() == 34

def test_something():
    x = Variable()

    y = x >> fn_node(which_func)()
    z = x >> fn_node(which_func)()
    g = Graph(x, [y, z])
    y_out, z_out = g.run({ x: 10 })
    assert y_out == z_out

def test_func_node():
    x = Variable()
    y = Variable()
    z = Variable()
    func_node = fn_node(what_func)()(x, y, z)
    g = Graph([x,y,z], func_node)
    result = g.run({
        x : 1,
        y : 2,
        z : 3
    })
    assert(result == 5)
