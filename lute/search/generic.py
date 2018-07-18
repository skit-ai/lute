"""
Generic search handler
"""

from typing import Dict, List

from lute.node import Node


class ExpansionSearch(Node):
    """
    Class for expansion based search
    """

    def __init__(self, terms: List[str], exp: Dict):
        super().__init__()
        self._name = ExpansionSearch.__gen_name__()
        self.terms = terms
        self.exp = exp
        self._validate_expansions()

    def _validate_expansions(self):
        """
        Check if all the terms are in the expansion dict
        """

        for term in self.terms:
            if term not in self.exp:
                raise KeyError("Term {} not found in expansion dict".format(term))

    def __call__(self, other: Node):
        super().__call__(other)
        self._text_node = other

        return self

    def _term_present(self, term: str) -> bool:
        return any([form in self._text_node.value for form in self.exp[term]])

    def eval(self):
        """
        Search for terms based on expansion
        NOTE: This assume untokenized string as of now
        """

        self._output_val = [
            term for term in self.terms if self._term_present(term)
        ]
