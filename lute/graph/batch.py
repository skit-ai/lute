"""
Stuff for working with batches of data
"""


from typing import List

from lute.graph import Graph


def batch_eval(g: Graph, input_batch: List) -> List:
    return [g.run(ip) for ip in input_batch]
