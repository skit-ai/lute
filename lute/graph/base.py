from copy import deepcopy
from typing import Any, Dict, List, Tuple, Union

from pydash import py_

from lute.node import GraphNode, Node, Variable
from lute.node.utils import resolve, walk_node

GraphInput = Union[List[Node], Node]
GraphOutput = Union[List[Node], Node]

NodeId = Union[Node, str]
Param = Union[Tuple[NodeId, str], str]


class Graph:
    """
    A DAG with some input and output nodes
    """

    def __init__(self, input: GraphInput, output: GraphOutput):
        self.inputs = input if isinstance(input, list) else [input]
        self.outputs = output if isinstance(output, list) else [output]
        self._nodes = self._all_nodes()
        self._nodes_map = {n.name_str(): n for n in self._nodes}

    def _all_nodes(self):
        return py_.uniq(self._forward_nodes() + self._backward_nodes() + self.inputs + self.outputs)

    def _forward_nodes(self):
        return py_.uniq(py_.flatten([walk_node(n) for n in self.inputs]))

    def _backward_nodes(self):
        return py_.uniq(py_.flatten([walk_node(n, backward=True) for n in self.outputs]))

    def set_param(self, param: Union[Param, str], value: Any):
        n, attr = self._resolve_param_node(param)
        setattr(n, attr, value)

    def _resolve_param_node(self, param: Union[Param, str]) -> Tuple[Node, str]:
        if isinstance(param, str):
            valid_nodes = [n for n in self._nodes if hasattr(n, param)]
            if len(valid_nodes) == 1:
                return valid_nodes[0], param
            else:
                raise Exception("Unable to resolve param target")
        else:
            return self._nodes_map[param[0].name_str()], param[1]

    def resolve_node(self, i: NodeId):
        return resolve(i, self._nodes)

    def subgraph(self, inputs: List[NodeId] = None, outputs: List[NodeId] = None):
        """
        Return a sub graph based on the io node identifiers
        """

        if inputs is None:
            inputs = self.inputs
        else:
            inputs = [self.resolve_node(i) for i in inputs]

        if outputs is None:
            outputs = self.outputs
        else:
            outputs = [self.resolve_node(o) for o in outputs]

        return Graph(inputs, outputs)

    def clone(self):
        return deepcopy(self)

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
