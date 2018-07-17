from typing import List, Dict, Any
from lute.node import Node, Variable


class Graph:
    """
    Class for a runnable graph
    """

    def __init__(self, inputs: List[Node], outputs: List[Node]):
        self._inputs = inputs
        self._outputs = outputs

    def run(self, values_dict: Dict[Variable, Any] = {}):
        """
        Run the values
        """

        for node in values_dict:
            if isinstance(node, Variable) and node in self._inputs:
                node.value = values_dict[node]

        return [output.value for output in self._outputs]
