"""
Function to node transformer
"""

import ast
import inspect

from lute.node.base import Node, NodeMeta


class ValueTransformer(ast.NodeTransformer):
    """
    Change desired variables to variables.value
    """

    def __init__(self, input_ids):
        super().__init__()
        self._input_ids = input_ids

    def visit_Name(self, node):
        if node.id in self._input_ids:
            return ast.Call(
                func=ast.Name(id="getattr", ctx=ast.Load()),
                args=[node, ast.Str("value")],
                keywords=[]
            )
        else:
            return node


def fn_node(fn) -> Node:
    """
    Convert the function to a node
    """

    name = fn.__name__
    args = inspect.getfullargspec(fn).args

    # Patch function
    tree = ast.parse(inspect.getsource(fn))
    tree = ValueTransformer(args).visit(tree)
    ast.fix_missing_locations(tree)

    namespace = {}
    exec(compile(tree, filename="<ast>", mode="exec"), namespace)

    def __init__(self):
        pass

    def __call__(self, *args):
        self._register_predecessors(args)
        self._input = args
        return self

    Cls = NodeMeta(name, (Node,), {
        "__init__": __init__,
        "__call__": __call__,
        "eval": lambda self: namespace[name](*self._input)
    })

    def _wrapper(*args):
        return Cls(*args)

    return _wrapper
