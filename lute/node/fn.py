"""
Function to node transformer
"""

import ast
import inspect
from uuid import uuid4

from lute.node.base import Node, NodeMeta


class NameTransformer(ast.NodeTransformer):
    """
    Change the name of function (in definition)
    """

    def __init__(self, old_name, new_name):
        super().__init__()
        self.old_name = old_name
        self.new_name = new_name

    def visit_FunctionDef(self, node):
        if node.name == self.old_name:
            return ast.FunctionDef(
                name=self.new_name,
                args=node.args,
                body=node.body,
                decorator_list=node.decorator_list,
                returns=node.returns
            )
        else:
            return node


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


def unique_name(root: str) -> str:
    return "{}__{}".format(root, str(uuid4()).replace("-", "_"))


def fn_node(fn) -> Node:
    """
    Convert the function to a node
    """

    name = fn.__name__
    global_namespace = fn.__globals__
    args = inspect.getfullargspec(fn).args

    # Assign new name to avoid collision
    new_name = unique_name(name)

    # Patch function
    tree = ast.parse(inspect.getsource(fn))
    tree = ValueTransformer(args).visit(tree)
    tree = NameTransformer(name, new_name).visit(tree)
    ast.fix_missing_locations(tree)

    exec(compile(tree, filename="<ast>", mode="exec"), global_namespace)

    def __init__(self):
        pass

    def __call__(self, *args):
        self._register_predecessors(list(args))
        self._input = args
        return self

    return NodeMeta(unique_name(name), (Node,), {
        "__init__": __init__,
        "__call__": __call__,
        "eval": lambda self: global_namespace[new_name](*self._input)
    })
