"""
Visualization for graph
"""

from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import networkx as nx

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


def plot_graph(g: Graph, **kwargs):
    nxg = make_nx_graph(g)
    fig, ax = plt.subplots(**kwargs)

    pos = nx.spring_layout(nxg)

    nx.draw_networkx_edges(nxg, pos, ax=ax, edgelist=nxg.edges, alpha=0.5)
    nx.draw_networkx_nodes(nxg, pos, ax=ax, nodelist=g.inputs, node_color="#1abc9c")
    nx.draw_networkx_nodes(nxg, pos, ax=ax, nodelist=g.outputs, node_color="#3498db")
    intermittent_nodes = [n for n in nxg.nodes if n not in g.inputs + g.outputs]
    nx.draw_networkx_nodes(nxg, pos, ax=ax, nodelist=intermittent_nodes,
                           node_color="#95a5a6", node_shape="o", with_labels=True)

    nx.draw_networkx_labels(nxg, pos, ax=ax, labels={n: repr(n) for n in nxg.nodes}, alpha=0.7)
    plt.axis("off")
    plt.show()
