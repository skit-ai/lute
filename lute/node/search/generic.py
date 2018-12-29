"""
Generic search handler
"""

import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import regex as re
from lute.node import Node

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


def make_optional_pattern(items: List[str], word_break=True) -> str:
    if word_break:
        return re.compile(r"\b" + r"\b|\b".join(items) + r"\b", re.I | re.UNICODE)
    else:
        return re.compile(r"(" + r")|(".join(items) + r")", re.I | re.UNICODE)


def replace_subexpr(pattern: str, expansions: Dict[str, List[str]]) -> str:
    """
    Replace subexpr in pattern using the expansions and return the new pattern
    """

    ranges = []
    replacements = []
    for m in re.finditer("\{EX:(?P<subexpr>.+?)}", pattern, flags=re.I | re.UNICODE):
        term = m.group("subexpr")
        span = m.span("subexpr")
        ranges.append((span[0] - 4, span[1] + 1))

        if term not in expansions:
            warnings.warn(f"Term {term} not found in expansions")
            replacements.append("")
        else:
            replacements.append(make_optional_pattern(expansions[term], word_break=False).pattern)

    return range_replace(pattern, ranges, replacements)


class PatternMatch(Node):
    """
    Pattern matching node. Allow sub expressions like the following:
    - {EX:term} expands the term's expansion
    - ...
    """

    def __init__(self, cls_patterns: Dict[str, List[str]], expansions: Dict[str, List[str]] = None):
        self.expansions = expansions
        self.patterns = self._prepare_patterns(cls_patterns)

    def _prepare_patterns(self, cls_patterns: Dict[str, List[str]]):
        final_patterns = {}
        for cls, patterns in cls_patterns.items():
            if self.expansions:
                patterns = [replace_subexpr(it, self.expansions) for it in patterns]

            final_patterns[cls] = make_optional_pattern(patterns, word_break=False)

        return final_patterns

    def eval(self, text: Node):
        if not text.value:
            return []

        # Run through all the patterns
        classes = []
        for cls in self.patterns:
            match = self.patterns[cls].search(text.value)
            if match:
                span = match.span()
                score = (span[1] - span[0]) / len(text.value)
                # TODO: Remove this filtering since this case should not be there.
                #       Mostly we might have been thinking about some edge case without
                #       noting that down somwhere
                if score > 0:
                    classes.append((cls, score))

        return sorted(classes, key=lambda c: c[1], reverse=True)


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
