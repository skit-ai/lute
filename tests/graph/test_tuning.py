from lute.graph import Graph
from lute.graph.tuning import list_sampler, single_search
from lute.node import Node, Variable


class PowNode(Node):
    def __init__(self):
        self.alpha = None

    def __call__(self, other: Node):
        self._register_predecessors([other])

        self.other = other
        return self

    def eval(self):
        return self.other.value ** self.alpha


def test_tuning():
    batch = [-1, 2, 3, 4, -3]

    x = Variable()
    g = Graph(x, x >> PowNode())

    sampler = list_sampler([x * 0.1 for x in range(10)])
    output = single_search(g, batch, "alpha", sampler, lambda ys: abs(sum(ys)))
    best = max(output, key=lambda x: x[1])

    assert best[0] == 0.4
