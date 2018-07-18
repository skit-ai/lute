from typing import List, Dict, Any, Union
from lute.node import Node, Variable

GraphInput = Union[List[Node], Node]
GraphOutput = Union[List[Node], Node]

class Graph:
    """
    A DAG with some input and output nodes
    """

    def __init__(self, input: GraphInput, output: GraphOutput):
        self.inputs = input if type(input) == list else [input]
        self.outputs = output if type(output) == list else [output]


    def run(self, values_dict: Dict[Variable, Any] = {}):
        """
        Run the values
        """

        for node in values_dict:
            if isinstance(node, Variable) and node in self.inputs:
                node.value = values_dict[node]

        return [output.value for output in self.outputs]
