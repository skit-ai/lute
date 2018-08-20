"""
Function to node transformer
"""

import ast
import inspect
from textwrap import dedent
from uuid import uuid4

from lute.node.base import Constant, Node, NodeMeta


def is_lambda(v) -> bool:
    """
    Check for lambda. From https://stackoverflow.com/a/3655857
    """

    LAMBDA = lambda: 0
    return isinstance(v, type(LAMBDA)) and v.__name__ == LAMBDA.__name__


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


class AssignTransformer(ast.NodeTransformer):
    """
    Add another assign statement to copy the value of the Variable into a local variable.
    Variable.id : local_variable.id is stored in visited_assigned_nodes
    """

    def __init__(self, input_ids, visited_assigned_nodes):
        super().__init__()
        self._input_ids = input_ids
        self.visited_assigned_nodes = visited_assigned_nodes
        self.reverse_mapping = dict((v, k) for k, v in visited_assigned_nodes.items())

    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Tuple):
            target_nodes = node.targets[0].elts
        else:
            target_nodes = [node.targets[0]]
        new_assign_nodes = []
        for name_node in target_nodes:
            if name_node.id in self.visited_assigned_nodes.values():
                new_assign_node = ast.Assign(
                    targets=[ast.Name(id=name_node.id, ctx=ast.Store())],
                    value=ast.IfExp(
                        test=ast.Call(
                            func=ast.Name(id="isinstance", ctx=ast.Load()),
                            args=[
                                ast.Name(id=self.reverse_mapping[name_node.id], ctx=ast.Load()),
                                ast.Name(id="Node", ctx=ast.Load()),
                            ],
                            keywords=[],
                        ),
                        body=ast.Call(
                            func=ast.Name(id="getattr", ctx=ast.Load()),
                            args=[
                                ast.Name(id=self.reverse_mapping[name_node.id], ctx=ast.Load()),
                                ast.Str(s="value"),
                            ],
                            keywords=[],
                        ),
                        orelse=ast.Name(id=self.reverse_mapping[name_node.id], ctx=ast.Load()),
                    )
                )
                new_assign_nodes.append(new_assign_node)

        nodes_to_return = []
        nodes_to_return.extend(new_assign_nodes)
        nodes_to_return.append(node)
        return nodes_to_return


class ValueTransformer(ast.NodeTransformer):
    """
    Change desired variables to variables.value
    """

    def __init__(self, input_ids):
        super().__init__()
        self._input_ids = input_ids
        self.visited_assigned_nodes = {}

    def visit_Name(self, node):
        if node.id in self._input_ids:
            # If the parent node is an Assign node, replace it with variable.value with Store() context
            if (isinstance(node.parent, ast.Assign) or (
                    isinstance(node.parent, ast.Tuple) and isinstance(node.parent.parent, ast.Assign))):
                if (node.id not in self.visited_assigned_nodes.keys()):
                    self.visited_assigned_nodes[node.id] = node.id

                return ast.Name(id=self.visited_assigned_nodes[node.id], ctx=ast.Store())

            # If the parent node is not an assign node, replace it with getattr()
            elif (not isinstance(node.parent, ast.Assign)):
                if (node.id in self.visited_assigned_nodes.keys()):
                    return ast.Name(id=self.visited_assigned_nodes[node.id], ctx=ast.Load())

                return ast.Call(
                    func=ast.Name(id="getattr", ctx=ast.Load()),
                    args=[node, ast.Str("value")],
                    keywords=[]
                )
        else:
            return node


def unique_name(root: str) -> str:
    return "{}__{}".format(root, str(uuid4()).replace("-", "_"))


def node_fn(*args, **kwargs):
    """
    Convert the node to a plain callable function
    """

    def _get_instance(it, *args, **kwargs):
        if isinstance(it, Node):
            return it
        elif isinstance(it, NodeMeta):
            return it(*args, **kwargs)
        else:
            return None

    def _get_wrapper(inst):
        def _wrapper(*args, **kwargs):
            c_args = [Constant(v) for v in args]
            c_kwargs = {k: Constant(kwargs[k]) for k in kwargs}
            inst(*c_args, **c_kwargs)
            return inst.eval()

        return _wrapper

    if len(args) == 1 and len(kwargs) == 0:
        instance = _get_instance(args[0])
        if instance is not None:
            return _get_wrapper(instance)

    # These are args, wrap another function now
    def _decorator(node: Node):
        instance = _get_instance(node, *args, **kwargs)
        return _get_wrapper(instance)

    return _decorator


def fn_node(fn) -> Node:
    """
    Convert the function to a node
    """

    if is_lambda(fn):
        raise Exception("lambdas are not supported as of now, please don't be lazy")

    name = fn.__name__
    global_namespace = fn.__globals__
    global_namespace["Node"] = Node
    args = inspect.getfullargspec(fn).args

    # Assign new name to avoid collision
    new_name = unique_name(name)

    # Patch function
    tree = ast.parse(dedent(inspect.getsource(fn)))

    # Create a pointer to the parent node in the tree
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node

    trans_obj = ValueTransformer(args)
    tree = trans_obj.visit(tree)
    tree = AssignTransformer(args, trans_obj.visited_assigned_nodes).visit(tree)
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
