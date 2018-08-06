"""
Basic feature extractors
"""

import requests
from pydash import py_

from lute.node import Node


class NGrams(Node):
    """
    N-grams keeping features which match the given list (at least one token)
    """

    def __init__(self, ns=(1, 2)):
        self.ns = (ns,) if isinstance(ns, int) else ns

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


class POSTagger(Node):
    """
    SyntaxNet node
    """

    def __init__(self, root_url: str, lang: str):
        self.root_url = root_url
        self.lang = lang

    def __call__(self, text: Node):
        self._register_predecessors([text])
        self._text = text

        return self

    def eval(self):
        req = requests.post(
            self.root_url,
            data=self._text.value.encode('utf-8'),
            headers={"Content-Type": "text/plain"}
        )
        return req.json()[0]
