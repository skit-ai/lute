"""
Visualization for graph
"""

import networkx as nx
from lute.graph.graph import Graph


def make_nx_graph(g: Graph) -> nx.DiGraph:
    dg = nx.DiGraph()

    seen = []
    edges = []
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
