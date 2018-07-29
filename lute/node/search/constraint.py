"""
Constraint finding nodes
"""

from typing import Any, Dict, List, Tuple

from pydash import py_

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

        results = [(c, self._missing_keys(c)) for c in self.constraints]

        if self.partial:
            return py_.filter(results, lambda it: len(it[1]) < len(it[0]))
        else:
            return py_.filter(results, lambda it: len(it[1]) == 0)
