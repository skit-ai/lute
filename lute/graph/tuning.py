from typing import List

from lute.graph import Graph
from lute.graph.batch import batch_eval


def list_sampler(values: List):
    def _sampler():
        idx = 0
        while idx < len(values):
            yield values[idx]
            idx += 1

    return _sampler


def single_search(g: Graph, input_batch: List, param, sampler, summary_fn):
    """
    Single param search function
    """

    output = []

    for v in sampler():
        g.set_param(param, v)
        output.append((v, summary_fn(batch_eval(g, input_batch))))

    return output
