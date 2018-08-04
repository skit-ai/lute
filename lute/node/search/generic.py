"""
Generic search handler
"""

from typing import Any, Dict, List

import regex as re

from lute.node import Node


class ExpansionSearch(Node):
    """
    Class for expansion based search
    """

    def __init__(self, terms: List[str], exp: Dict, lang: str = "en", regex=True):
        self.terms = terms
        self.exp = exp
        self.lang = lang
        self.search_type = "expansion"
        self._validate_expansions()
        if regex is False:
            self._escape_expansions()
        self._prepare_matcher()

    def _validate_expansions(self):
        """
        Check if all the terms are in the expansion dict
        """

        for term in self.terms:
            try:
                self.exp[term]
            except KeyError:
                raise KeyError("Term {} not found in expansion dict".format(term))

    def _escape_expansions(self):
        """
        Escape expansions to avoid regexy characters
        """

        for term in self.terms:
            escaped = [re.escape(form) for form in self.exp[term]]
            self.exp[term] = escaped

    def _prepare_matcher(self):
        """
        Precompile regex for the relevant expansions
        """

        self.re_patterns = {}
        for term in self.terms:
            self.re_patterns[term] = re.compile(r"\b" + r"\b|\b".join(self.exp[term]) + r"\b", re.I | re.UNICODE)

    def __call__(self, other: Node):
        self._register_predecessors([other])
        self._text_node = other

        return self

    def _get_matches(self, term: str) -> List[Any]:
        return list(self.re_patterns[term].finditer(self._text_node.value))

    def eval(self):
        """
        Search for terms based on expansions
        NOTE: This assume antagonized strings
        """

        results = []
        for term in self.terms:
            matches = self._get_matches(term)
            print(matches)
            results.extend([{
                "type": self.search_type,
                "value": term,
                "range": (m.span()[0], m.span()[1])
            } for m in matches])

        return results


class ListSearch(ExpansionSearch):
    """
    Class for searching based on a list of words/phrases
    """

    def __init__(self, terms: List[str], lang: str = "en"):
        super().__init__(terms, self._generate_expansions(terms), lang=lang, regex=False)
        self.search_type = "list"

    def _generate_expansions(self, terms):
        return {k: [k] for k in terms}


class Canonicalize(Node):
    """
    Use the search results on the string to convert in a canonical form.
    """

    def __init__(self, remove_duplicates=False):
        self.remove_duplicates = remove_duplicates

    def __call__(self, text: Node, search_results: Node):
        self._register_predecessors([text, search_results])
        self._text_node = text
        self._search_results = search_results

        return self

    def _filter_searches(self):
        """
        In case of overlaps, keep the larger result
        """

        def _overlap_p(res1, res2):
            first, second = (res1, res2) if res1["range"][0] < res2["range"][0] else (res2, res1)
            return first["range"][1] >= second["range"][0]

        ordered = sorted(self._search_results.value, key=lambda res: res["range"][1] - res["range"][0], reverse=True)

        filtered = []
        matched = set()

        for it in ordered:
            # NOTE: There are optimizations possible but are not important at the moment
            if self.remove_duplicates and it["value"] in matched:
                it_copy = it.copy()
                it_copy["value"] = ""
                filtered.append(it_copy)
            elif not any([_overlap_p(it, fit) for fit in filtered]):
                matched.add(it["value"])
                filtered.append(it)

        return sorted(filtered, key=lambda res: res["range"][0])

    def _mutate(self, searches):
        offset = 0
        text = list(self._text_node.value)
        for search in searches:
            rng = search["range"]
            replacement = list(search["value"])
            text[rng[0] - offset:rng[1] - offset] = list(replacement)
            offset += (rng[1] - rng[0]) - len(replacement)

        return "".join(text)

    def eval(self):
        return " ".join(self._mutate(self._filter_searches()).split())
