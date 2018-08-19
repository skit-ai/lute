from typing import Any, Dict, List, Union

from pydash import py_

from lute.node import GraphNode, Node, Variable
from lute.node.utils import walk_node

GraphInput = Union[List[Node], Node]
GraphOutput = Union[List[Node], Node]


class Graph:
    """
    A DAG with some input and output nodes
    """

    def __init__(self, input: GraphInput, output: GraphOutput):
        self.inputs = input if isinstance(input, list) else [input]
        self.outputs = output if isinstance(output, list) else [output]
        self._nodes = self._all_nodes()

    def _all_nodes(self):
        return py_.uniq(self._forward_nodes() + self._backward_nodes())

    def _forward_nodes(self):
        return py_.uniq(py_.flatten([walk_node(n) for n in self.inputs]))

    def _backward_nodes(self):
        return py_.uniq(py_.flatten([walk_node(n, backward=True) for n in self.outputs]))

    def clear(self):
        """
        Clear all involved nodes
        """

        for node in self._nodes:
            node.clear()

    def run(self, input_values=None, values_dict: Dict[Variable, Any] = None):
        """
        Run the values
        """

        self.clear()

        if input_values is None:
            input_values = []

        if values_dict is not None:
            for node in values_dict:
                if isinstance(node, Variable) and node in self.inputs:
                    node.value = values_dict[node]
        else:
            valid_inputs = [node for node in self.inputs if isinstance(node, Variable)]
            if len(valid_inputs) == 1:
                valid_inputs[0].value = input_values
            else:
                if len(valid_inputs) == len(input_values):
                    for node, val in zip(valid_inputs, input_values):
                        node.value = val
                else:
                    raise Exception("Input values length not matching length of graph inputs")

        results = [output.value for output in self.outputs]

        return results[0] if len(results) == 1 else results


def graph_node(g: Graph) -> Node:
    return GraphNode(g)
