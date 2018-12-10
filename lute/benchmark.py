"""
Module for attaching benchmarking code to graph and nodes
"""

import time

from lute.graph import Graph
from lute.node import Node


def patch_node(node: Node):
    """
    Patch the node to keep timing info for the eval function
    """

    if hasattr(node, "benchmark"):
        raise RuntimeError(f"Node {node} already has benchmarking code")

    node.benchmark = {}
    eval_fn = node.eval

    def _bm_eval_fn(*args, **kwargs):
        start = time.time()
        out = eval_fn(*args, **kwargs)
        end = time.time()
        node.benchmark["eval_time"] = end - start
        return out

    node.eval = _bm_eval_fn


def patch_graph(g: Graph):
    """
    Patch the graph to keep timing info
    """

    if hasattr(g, "benchmark"):
        raise RuntimeError(f"Graph {g} already as benchmarking code")

    g.benchmark = {}
    run_fn = g.run

    for node in g._nodes:
        patch_node(node)

    def _bm_run_fn(*args, **kwargs):
        start = time.time()
        out = run_fn(*args, **kwargs)
        end = time.time()
        g.benchmark["run_time"] = end - start
        return out

    g.run = _bm_run_fn


def calculate_self_time_node(node: Node):
    """
    Calculate self eval time for the node
    """

    if not hasattr(node, "benchmark"):
        raise RuntimeError(f"Node {node} is not patched with benchmarking code")

    if node.predecessors:
        for par_node in node.predecessors:
            calculate_self_time_node(par_node)
        # TODO: This might be wrong. We are assuming a few things about the runtime
        #       behavior of the graph.
        parent_time = sum([par_node.benchmark["eval_time"] for par_node in node.predecessors])
    else:
        parent_time = 0

    node.benchmark["self_eval_time"] = node.benchmark["eval_time"] - parent_time


def calculate_self_time_graph(g: Graph):
    """
    Use the logged time in graph to calculate self eval time for each node.
    Also attach that information to the graph.
    """

    if not hasattr(g, "benchmark"):
        raise RuntimeError(f"Graph {g} is not patched with benchmarking code")

    for node in g._nodes:
        calculate_self_time_node(node)
