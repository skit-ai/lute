"""
Visualization for graph
"""

import json
import os
import webbrowser
from typing import Dict

import pkg_resources
from lute.benchmark import graph_has_benchmark
from lute.graph.base import Graph
from lute.node.base import Node


def generate_dagre_data(g: Graph) -> Dict:
    """
    Generate json data for dagre
    """

    add_benchmark = graph_has_benchmark(g)

    def _node_to_dict(node: Node) -> Dict:
        if node in g.inputs:
            node_type = "input"
        elif node in g.outputs:
            node_type = "output"
        else:
            node_type = None

        return {
            **node.to_dict(),
            "name": node.name_str(),
            "type": node_type,
            "times": node.benchmark.get("self_eval_times") if add_benchmark else None
        }

    graph = {
        "nodes": [],
        "edges": []
    }

    visited = []
    todo = g.inputs + g.outputs

    while len(todo) > 0:
        node = todo.pop()
        graph["nodes"].append(node)
        visited.append(node)
        succ = [n for n in node.successors if n not in visited]
        graph["edges"] += [(node, s) for s in succ]
        pred = [n for n in node.predecessors if n not in visited]
        graph["edges"] += [(p, node) for p in pred]
        todo += (succ + pred)

    graph["nodes"] = [_node_to_dict(n) for n in graph["nodes"]]
    graph["edges"] = [(x.name_str(), y.name_str()) for x, y in graph["edges"]]

    return graph


def plot_graph(g: Graph, json_encoder=None, open_browser=True):
    """
    Create visualization for the given graph. If provided, pass given encoder
    class in json.dumps.
    """

    serve_dir = pkg_resources.resource_filename("lute", "viz-js")

    with open(os.path.join(serve_dir, "data.js"), "w", encoding='utf-8') as fp:
        fp.write("let data = {}".format(json.dumps(generate_dagre_data(g), cls=json_encoder, indent=2)))

    if open_browser:
        webbrowser.open("file://" + os.path.join(serve_dir, "index.html"))
