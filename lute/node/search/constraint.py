"""
Constraint finding nodes
"""

from typing import Any, Dict, List, Tuple

from pydash import py_
from sklearn.feature_extraction.text import TfidfVectorizer

from lute.node import Node

Constraint = Dict[str, Any]


class ConstraintSearch(Node):
    """
    Return what constraints are satisfied. A constraint is a dict with a str mapping
    to a value.
    """

    def __init__(self, cs: List[Constraint], partial=False):
        self.constraints = cs
        self.partial = partial
        self.keys = self._find_all_keys()

    def _find_all_keys(self) -> List[str]:
        return py_.uniq(py_.flatten([list(c.keys()) for c in self.constraints]))

    def __call__(self, input_map: Dict[str, Node]):
        if any([key not in input_map for key in self.keys]):
            raise KeyError("Not all constraint keys present in input map")

        self._register_predecessors(list(input_map.values()))
        self._input_map = input_map

        return self

    def _missing_keys(self, c: Constraint) -> List[str]:
        missing = []

        for key in c:
            if c[key] is not None:
                values = [it["value"] for it in self._input_map[key].value]
                if c[key] not in values:
                    missing.append(key)

        return missing

    def eval(self):
        """
        Return constraints and missing keys
        """

        results = [{ "constraint": c, "missing": self._missing_keys(c) } for c in self.constraints]

        if self.partial:
            return py_.filter(results, lambda it: len(it["missing"]) < len(it["constraint"]))
        else:
            return py_.filter(results, lambda it: len(it["missing"]) == 0)


class RankConstraints(Node):
    """
    Rank constraints using some heuristics
    NOTE: We are not giving priority to lengths
    """

    def __init__(self):
        pass

    def __call__(self, constraints: ConstraintSearch):
        self._register_predecessors([constraints])
        self._cons_node = constraints

        return self

    def _match_score(self, constraint):
        """
        Return direct match score
        """

        total = len(constraint["constraint"])
        return 1 - (len(constraint["missing"]) / total)

    def _disambiguate(self, ranked, tf_scores):
        """
        Order items based on match importance,
        NOTE, we are not currently changing the scores here
        """

        grouped_score = py_.group_by(zip(ranked, tf_scores), lambda it: it[0]["score"])

        output = []

        for score in grouped_score:
            lfn = lambda it: len(it[0]["constraint"])
            grouped_length = py_.group_by(sorted(grouped_score[score], key=lfn, reverse=True), lfn)
            for length in grouped_length:
                items = sorted(grouped_length[length], key=lambda it: it[1], reverse=True)
                output += [c for c, _ in items]

        return output

    def eval(self):
        ranked = sorted([{**c, "score": self._match_score(c)} for c in self._cons_node.value],
                        key=lambda c: c["score"], reverse=True)

        tf = TfidfVectorizer().fit_transform([" ".join(c["constraint"].values()) for c in ranked])
        tf_scores = tf.todense().sum(axis=1)

        return self._disambiguate(ranked, tf_scores)
