from lute.node import Node
from yamraz.tokenizer import tokenize


class Tokenizer(Node):

    def __init__(self, language):
        super().__init__()
        self._name = Tokenizer.__gen_name__()
        self._lang = language

    def __call__(self, other: Node):
        super().__call__(other)
        if isinstance(other.value, str):
            self._text_node = other
        else:
            raise Exception("Type Mismatch: Expected str got %s" % type(other.value))

        return self

    def eval(self):
        return tokenize(self._text_node.value, self._lang)
