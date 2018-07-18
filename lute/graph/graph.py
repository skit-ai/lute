from typing import List, Dict, Any, Union
from lute.node import Node, Variable
from lute.graph.utils import walk_node
from pydash import py_

GraphInput = Union[List[Node], Node]
GraphOutput = Union[List[Node], Node]


class Graph:
    """
    A DAG with some input and output nodes
    """

    def __init__(self, input: GraphInput, output: GraphOutput):
        self.inputs = input if type(input) == list else [input]
        self.outputs = output if type(output) == list else [output]
        self._nodes = self._all_nodes()

    def _all_nodes(self):
        return self._forward_nodes() + self._backward_nodes()

    def _forward_nodes(self):
        return py_.uniq(py_.flatten([walk_node(n) for n in self.inputs]))

    def _backward_nodes(self):
        return py_.uniq(py_.flatten([walk_node(n, backward=True) for n in self.outputs]))

    def run(self, values_dict: Dict[Variable, Any] = {}):
        """
        Run the values
        """

        # Clear values for all involved nodes
        for node in self._nodes:
            node.clear()

        for node in values_dict:
            if isinstance(node, Variable) and node in self.inputs:
                node.value = values_dict[node]

        return [output.value for output in self.outputs]
