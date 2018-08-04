"""
Basic feature extractors
"""

from pydash import py_

from lute.node import Node


class NGrams(Node):
    """
    N-grams keeping features which match the given list (at least one token)
    """

    def __init__(self, ns=(1, 2)):
        self.ns = (ns,) if type(ns) == int else ns

    def __call__(self, tokenizer: Node, allowed_items: Node = None):
        if allowed_items is None:
            self._register_predecessors([tokenizer])
        else:
            self._register_predecessors([tokenizer, allowed_items])

        self._tokenizer = tokenizer
        self._allowed_items = allowed_items

        return self

    def _generate_ngrams(self, tokens, n):
        ngrams = []
        for i in range(0, len(tokens) - n + 1):
            ngrams.append(tuple(tokens[i:(i + n)]))
        return ngrams

    def eval(self):
        """
        Create ngrams and filter using allowed_items
        """

        ngrams = []
        tokens = self._tokenizer.value

        for n in self.ns:
            ngrams.extend(self._generate_ngrams(tokens, n))

        if self._allowed_items is not None:
            ngrams = py_.filter(ngrams, lambda ng: any([tk in self._allowed_items.value for tk in ng]))

        return ngrams
