"""
Constraint finding nodes
"""

from typing import List

from lute.node import Node


class ConstraintSearch(Node):
    """
    Return what constraints are satisfied
    """

    def __init__(self, constraints: List):
        self.constraints = self._filter_constraints(constraints)

    def _filter_constraints(self, constraints):
        if any([len(c) != len(constraints[0]) for c in constraints]):
            raise Exception("Not all constraints are of same length")

        return [
            constraint for constraint in constraints
            if any([c_it is not None for c_it in constraint])
        ]

    def __call__(self, others: List[Node]):
        if len(others) != len(self.constraints[0]):
            raise Exception("Length mismatch in input nodes and constraints")

        self._register_predecessors(others)
        self._other_nodes = others

        return self

    def _check_constraint(self, constraint) -> bool:
        for c_it, c_node in zip(constraint, self._other_nodes):
            if (c_it is not None) and (c_it not in c_node.value):
                return False

        return True

    def eval(self):
        """
        Return constraints that are fully satisfied
        """

        return [c for c in self.constraints if self._check_constraint(c)]
