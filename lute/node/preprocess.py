from yamraz.text import Text
from yamraz.tokenizer import tokenize

from lute.exceptions import TypeMismatchException
from lute.node import Node


class Tokenizer(Node):

    def __init__(self, language):
        self._lang = language

    def __call__(self, other: Node):
        self._register_predecessors([other])
        self._text_node = other

        return self

    def eval(self):
        _val = self._text_node.value
        if isinstance(_val, str):
            return tokenize(_val, self._lang)
        else:
            raise TypeMismatchException(str, type(_val))


class Normalizer(Node):

    def __init__(self, language):
        self._lang = language

    def __call__(self, other: Node):
        self._register_predecessors([other])
        self._text_node = other

        return self

    def eval(self):
        _val = self._text_node.value
        if isinstance(_val, str):
            return Text(_val, self._lang, normalize=True).text
        else:
            raise TypeMismatchException(str, type(_val))
