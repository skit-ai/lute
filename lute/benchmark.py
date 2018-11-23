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
