"""
Generic search handler
"""

import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import regex as re
from pydash import py_

from lute.node import Node

Pattern = Union[str, List[str]]
Range = Tuple[int, int]


def range_replace(text: str, ranges: List[Range], replacements: Optional[Union[List[str], str]] = None) -> str:
    """
    Replace the ranges given in text.

    TODO: This is NOT a complete implementation
          The correct implementation will check if the ranges are overlapping
          and will throw an error. In case you are using this function, make sure
          to only work with non-overlapping ranges.
    """

    if replacements is None:
        replacements = ""

    if isinstance(replacements, str):
        replacements = [replacements] * len(ranges)

    offset = 0
    for (start, end), rep in zip(sorted(ranges, key=lambda it: it[0]), replacements):
        text = text[:(start - offset)] + rep + text[(end - offset):]
        offset += (end - start) - len(rep)

    return text


def make_optional_pattern(items: List[str], word_break=True):
    if word_break:
        return re.compile(r"\b" + r"\b|\b".join(items) + r"\b", re.I | re.UNICODE)
    else:
        return re.compile(r"((" + r")|(".join(items) + r"))", re.I | re.UNICODE)


def replace_subexpr(pattern: str, expansions: Dict[str, List[str]]) -> str:
    """
    Replace subexpr in pattern using the expansions and return the new pattern
    """

    ranges = []
    replacements = []
    for m in re.finditer(r"\{EX:(?P<subexpr>.+?)}", pattern, flags=re.I | re.UNICODE):
        term = m.group("subexpr")
        span = m.span("subexpr")
        ranges.append((span[0] - 4, span[1] + 1))

        if term not in expansions:
            warnings.warn(f"Term {term} not found in expansions")
            replacements.append("")
        else:
            replacements.append(make_optional_pattern(expansions[term], word_break=False).pattern)

    return range_replace(pattern, ranges, replacements)


class Matcher:
    """
    Each matcher responds to one class.
    """

    def __init__(self, patterns: List[Pattern], expansions: Dict[str, List[str]] = None):
        self.patterns = [
            subpatts if isinstance(subpatts, list) else [subpatts]
            for subpatts in patterns
        ]

        self.negative_prefix = "~"
        self._validate_subpatts()

        if expansions:
            self._expand_patterns(expansions)

    def _validate_subpatts(self):
        """
        Check that there are not only negatives in subpatts
        """

        for subpatts in self.patterns:
            if all(patt.startswith(self.negative_prefix) for patt in subpatts):
                raise RuntimeError("Cannot have all negative subpatterns.")

    def _expand_patterns(self, expansions):
        self.patterns = [
            [replace_subexpr(patt, expansions) for patt in subpatts]
            for subpatts in self.patterns
        ]

    def match(self, text: str):
        all_matches = []

        # We want all subpatts to match
        for subpatts in self.patterns:
            matches = []
            for patt in subpatts:
                negative = False
                if patt.startswith(self.negative_prefix):
                    patt = patt[1:]
                    negative = True

                match = re.search(patt, text, flags=re.I | re.U)

                if negative:
                    matches.append(not match)
                else:
                    matches.append(match)

            if all(matches):
                all_matches.extend(matches)

        all_matches = [m for m in all_matches if not isinstance(m, bool)]

        def _max_fn(m):
            span = m.span()
            return (span[1] - span[0]) / len(text)

        if all_matches:
            return max(all_matches, key=_max_fn)
        else:
            return None


class PatternMatch(Node):
    """
    Pattern matching node. Allow sub expressions like the following:
    - {EX:term} expands the term's expansion
    - ...
    """

    def __init__(self, cls_patterns: Dict[str, List[Pattern]], expansions: Dict[str, List[str]] = None):
        self.matchers = {cls: Matcher(patterns, expansions) for cls, patterns in cls_patterns.items()}

    def eval(self, text: Node):
        if not text.value:
            return []

        output = []
        for cls, matcher in self.matchers.items():
            match = matcher.match(text.value)
            if match:
                span = match.span()
                output.append({
                    "type": "pattern",
                    "name": cls,
                    "score": (span[1] - span[0]) / len(text.value)
                })

        return sorted(output, key=lambda it: it["score"], reverse=True)


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
