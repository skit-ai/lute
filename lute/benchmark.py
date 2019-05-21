"""
Module for attaching benchmarking code to graph and nodes
"""

import time

from lute.graph import Graph
from lute.node import Node


def node_has_benchmark(node: Node) -> bool:
    return hasattr(node, "benchmark")


def graph_has_benchmark(g: Graph) -> bool:
    return hasattr(g, "benchmark") and all(node_has_benchmark(n) for n in g._nodes)


def patch_node(node: Node):
    """
    Patch the node to keep timing info for the eval function
    """

    if node_has_benchmark(node):
        raise RuntimeError(f"Node {node} already has benchmarking code")

    setattr(node, "benchmark", {"eval_times": [], "self_eval_times": []})
    eval_fn = node.eval

    def _bm_eval_fn(*args, **kwargs):
        blacklist = set()
        for par_node in node.predecessors:
            if par_node.evaluated:
                blacklist.add(par_node.id)

        start = time.time()
        out = eval_fn(*args, **kwargs)
        end = time.time()
        node.benchmark["eval_times"].append(end - start)

        par_time = 0
        for par_node in node.predecessors:
            if par_node.id not in blacklist:
                par_time += par_node.benchmark.get("eval_times", [0])[-1]

        node.benchmark["self_eval_times"].append(node.benchmark["eval_times"][-1] - par_time)
        return out

    setattr(node, "eval", _bm_eval_fn)


def patch_graph(g: Graph):
    """
    Patch the graph to keep timing info
    """

    if graph_has_benchmark(g):
        raise RuntimeError(f"Graph {g} already as benchmarking code")

    setattr(g, "benchmark", {"run_times": []})
    run_fn = g.run

    for node in g._nodes:
        patch_node(node)

    def _bm_run_fn(*args, **kwargs):
        start = time.time()
        out = run_fn(*args, **kwargs)
        end = time.time()
        g.benchmark["run_times"].append(end - start)
        return out

    setattr(g, "run", _bm_run_fn)
