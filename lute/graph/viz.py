"""
Visualization for graph
"""

import http.server
import json
import os
import socketserver
from typing import Dict, List, Tuple

import pkg_resources

from lute.graph.base import Graph
from lute.node.base import Node


def generate_dagre_data(g: Graph) -> Dict:
    """
    Generate json data for dagre
    """

    def _node_to_dict(node: Node) -> Dict:
        if node in g.inputs:
            node_type = "input"
        elif node in g.outputs:
            node_type = "output"
        else:
            node_type = None

        return {
            "name": node.name_str(),
            "value": node.value_str(),
            "type": node_type
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


def plot_graph(g: Graph, port=8999):
    serve_dir = pkg_resources.resource_filename("lute", "viz-js")

    with open(os.path.join(serve_dir, "data.json"), "w") as fp:
        json.dump(generate_dagre_data(g), fp)

    os.chdir(serve_dir)

    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), Handler)
    print("Serving at http://localhost:{}".format(port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
