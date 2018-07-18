"""
Visualization for graph
"""

import networkx as nx
from lute.graph.graph import Graph


def make_nx_graph(g: Graph) -> nx.DiGraph:
    dg = nx.DiGraph()

    for n in g.inputs + g.outputs:
        dg.add_node(n)

    for n in g.outputs:
        for in_n in n.predecessors:
            if in_n not in dg.nodes:
                dg.add_node(in_n)
            dg.add_edge(in_n, n)

    return dg
