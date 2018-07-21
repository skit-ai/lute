"""
Visualization for graph
"""

from typing import List, Tuple

import matplotlib.pyplot as plt
import networkx as nx
from lute.graph.base import Graph
from lute.node.base import Node


def make_nx_graph(g: Graph) -> nx.DiGraph:
    dg = nx.DiGraph()

    seen = []
    edges: List[Tuple[Node, Node]] = []
    todo = g.inputs + g.outputs

    while len(todo) > 0:
        node = todo.pop()
        dg.add_node(node)
        seen.append(node)
        succ = [n for n in node.successors if n not in seen]
        edges += [(node, s) for s in succ]
        pred = [n for n in node.predecessors if n not in seen]
        edges += [(p, node) for p in pred]
        todo += (succ + pred)

    for u, v in edges:
        dg.add_edge(u, v)

    return dg


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
