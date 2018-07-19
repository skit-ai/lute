from lute.node import Constant, Variable


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
