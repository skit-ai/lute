from lute.node import Node
from yamraz.tokenizer import tokenize


class Tokenizer(Node):

    def __init__(self, language):
        super().__init__()
        self._name = Tokenizer.__gen_name__()
        self._lang = language

    def __call__(self, other: Node):
        super().__call__(other)
        self._text_node = other

        return self

    def eval(self):
        _val = self._text_node.value
        if isinstance(_val, str):
            return tokenize(_val, self._lang)
        else:
            raise Exception("Type Mismatch: Expected str got %s" % type(_val))
