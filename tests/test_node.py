from lute.node import Constant, Variable


def test_name():
    c = Constant(2)
    assert c.name == 'Constant_0'

    c1 = Constant(3)
    assert c1.name == 'Constant_1'

    v = Variable()
    assert v.name == 'Variable_0'

    v1 = Variable()
    assert v1.name == 'Variable_1'
