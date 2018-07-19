"""
Generic search handler
"""

import re
from typing import Dict, List

from lute.node import Node


class ExpansionSearch(Node):
    """
    Class for expansion based search
    """

    def __init__(self, terms: List[str], exp: Dict):
        self.terms = terms
        self.exp = exp
        self._validate_expansions()
        self._prepare_matcher()

    def _prepare_matcher(self):
        """
        Precompile regex for the relevant expansions
        """

        self.re_patterns = {}
        for term in self.terms:
            self.re_patterns[term] = re.compile(r"\b" + r"\b|\b".join(self.exp[term]) + r"\b", re.I)

    def _validate_expansions(self):
        """
        Check if all the terms are in the expansion dict
        """

        for term in self.terms:
            if term not in self.exp:
                raise KeyError("Term {} not found in expansion dict".format(term))

    def __call__(self, other: Node):
        self._register_predecessors([other])
        self._text_node = other

        return self

    def _term_present(self, term: str) -> bool:
        return self.re_patterns[term].search(self._text_node.value) is not None

    def eval(self):
        """
        Search for terms based on expansions
        NOTE: This assume untokenized strings
        """

        return [
            term for term in self.terms if self._term_present(term)
        ]


class ListSearch(ExpansionSearch):
    """
    Class for searching based on a list of words/phrases
    """

    def __init__(self, terms: List[str]):
        super().__init__(terms, self._generate_expansions(terms))

    def _generate_expansions(self, terms):
        return {k: [k] for k in terms}
