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


def patch_node(node: Node, store_size=1000):
    """
    Patch the node to keep timing info for the eval function. Store size tells
    the max number of most recent eval_times saved.
    """

    if node_has_benchmark(node):
        raise RuntimeError(f"Node {node} already has benchmarking code")

    setattr(node, "benchmark", {"eval_times": [], "self_eval_times": [], "store_size": store_size})
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

        if len(node.benchmark["eval_times"]) > node.benchmark["store_size"]:
            # We will only have an excess of 1
            node.benchmark["eval_times"].pop(0)
            node.benchmark["self_eval_times"].pop(0)
        return out

    setattr(node, "eval", _bm_eval_fn)


def patch_graph(g: Graph, store_size=1000):
    """
    Patch the graph to keep timing info
    """

    if graph_has_benchmark(g):
        raise RuntimeError(f"Graph {g} already as benchmarking code")

    setattr(g, "benchmark", {"run_times": [], "store_size": store_size})
    run_fn = g.run

    for node in g._nodes:
        patch_node(node, store_size=store_size)

    def _bm_run_fn(*args, **kwargs):
        start = time.time()
        out = run_fn(*args, **kwargs)
        end = time.time()
        g.benchmark["run_times"].append(end - start)

        if len(g.benchmark["run_times"]) > g.benchmark["store_size"]:
            g.benchmark["run_times"].pop(0)
        return out

    setattr(g, "run", _bm_run_fn)
