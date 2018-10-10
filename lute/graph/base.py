import json
import warnings
from copy import deepcopy
from typing import Any, Dict, List, Tuple, Union

from pydash import py_

from lute.node import Node, Variable
from lute.node.utils import resolve, walk_node

GraphInput = Union[List[Node], Node]
GraphOutput = Union[List[Node], Node]

NodeId = Union[Node, str]
Param = Union[Tuple[NodeId, str], str]

GraphIdInput = Union[List[NodeId], NodeId]
GraphIdOutput = Union[List[NodeId], NodeId]


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

    def subgraph(self, input: GraphIdInput = None, output: GraphIdOutput = None):
        """
        Return a sub graph based on the io node identifiers
        """

        if input is None:
            inputs = self.inputs
        else:
            inputs = input if isinstance(input, list) else [input]
            inputs = [self.resolve_node(i) for i in inputs]

        # Patch inputs to be 0 fan-in type
        valid_inputs = []
        for n in inputs:
            if n.fan_in > 0:
                # Patch all the successors to connect a new input node
                n_p = Variable(name=n.name)

                warnings.warn("""
                Rewiring a node works on certain assumptions. The critical one right now is that
                all arguments in __call__ go directly in predecessors registration. If this is not the
                case, we will fail or the behavior will be undefined. There is a 'right' way to do
                this and we will be doing that some time.
                """)

                for succ in n.successors:
                    args = succ.predecessors
                    args[args.index(n)] = n_p
                    succ(*args)
                valid_inputs.append(n_p)
            else:
                valid_inputs.append(n)

        if output is None:
            outputs = self.outputs
        else:
            outputs = output if isinstance(output, list) else [output]
            outputs = [self.resolve_node(o) for o in outputs]

        return Graph(valid_inputs, outputs)

    def clone(self):
        return deepcopy(self)

    def clear(self):
        """
        Clear all involved nodes
        """

        for node in self._nodes:
            node.clear()

    def to_dict(self) -> Dict:
        raise NotImplementedError()

    def dumps(self) -> str:
        """
        Dump the value in json readable string.
        """

        return json.dumps(self.to_dict())

    def dumpb(self) -> bytes:
        """
        Dump to bytes. Default implementation just converts the output
        of dumps to bytes.
        """

        return bytes(self.dumps(), "utf-8")

    def run(self, *args, values_dict: Dict[Variable, Any] = None):
        """
        Run the values
        """

        self.clear()

        if values_dict is not None:
            # Dictionary assignment takes priority
            for node in values_dict:
                if isinstance(node, Variable) and node in self.inputs:
                    node.value = values_dict[node]
        else:
            valid_inputs = [node for node in self.inputs if isinstance(node, Variable)]
            if len(valid_inputs) == len(args):
                for node, val in zip(valid_inputs, args):
                    node.value = val
            elif len(args) == 1 and len(args[0]) == len(valid_inputs):
                for node, val in zip(valid_inputs, args[0]):
                    node.value = val
            else:
                raise Exception("Input values length not matching length of graph inputs")

        results = [output.value for output in self.outputs]

        return results[0] if len(results) == 1 else results
