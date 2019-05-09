import json

from lute.node import Constant


def test_serialization():
    class Dummy:
        pass

    c = Constant({1: Dummy()})
    c.value

    try:
        json.dumps(Dummy())
    except TypeError as e:
        message = str(e)

    assert json.loads(c.dumps())["value"] == message
