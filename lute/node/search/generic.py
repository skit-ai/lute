"""
Generic search handler
"""

from typing import Any, Dict, List, Tuple, Union

import regex as re
from lute.node import Node
from pydash import py_

Pattern = Union[str, List[str]]
Range = Tuple[int, int]


def make_optional_pattern(items: List[str], word_break=True):
    if word_break:
        return re.compile(r"\b(" + r"|".join(items) + r")\b", re.I | re.UNICODE)
    else:
        return re.compile(r"((" + r")|(".join(items) + r"))", re.I | re.UNICODE)


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
            self.re_patterns[term] = make_optional_pattern(self.exp[term])

    def _get_matches(self, term: str, text) -> List[Any]:
        return list(self.re_patterns[term].finditer(text))

    def eval(self, text: Node):
        """
        Search for terms based on expansions
        NOTE: This assume antagonized strings
        """

        results = []
        for term in self.terms:
            matches = self._get_matches(term, text.value)
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

    def eval(self, text: Node):
        return super().eval(text)

    def _generate_expansions(self, terms):
        return {k: [k] for k in terms}


class Canonicalize(Node):
    """
    Use the search results on the string to convert in a canonical form.
    """

    def __init__(self, remove_duplicates=False):
        self.remove_duplicates = remove_duplicates

    def _filter_searches(self, searches):
        """
        In case of overlaps, keep the larger result
        """

        def _overlap_p(res1, res2):
            first, second = (res1, res2) if res1["range"][0] < res2["range"][0] else (res2, res1)
            return first["range"][1] >= second["range"][0]

        ordered = sorted(searches, key=lambda res: res["range"][1] - res["range"][0], reverse=True)

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

    def _mutate(self, text, searches):
        offset = 0
        text = list(text)
        for search in searches:
            rng = search["range"]
            replacement = list(search["value"])
            text[rng[0] - offset:rng[1] - offset] = list(replacement)
            offset += (rng[1] - rng[0]) - len(replacement)

        return "".join(text)

    def eval(self, text: Node, search_results: Node):
        filtered_searches = self._filter_searches(search_results.value)
        return " ".join(self._mutate(text.value, filtered_searches).split())


class PickbestIntents(Node):
    """
    Group intents based on name and take the best ones
    """

    def eval(self, intents: Node):
        def _map_fn(intents):
            return max(intents, key=lambda it: it["score"])

        return py_.map(py_.group_by(intents.value, "name"), _map_fn)
