import time

import lute.benchmark as bm
from lute.graph import Graph
from lute.node import Constant, Node, Variable
from lute.node.fn import node_fn


class DizzyNode(Node):
    def __init__(self, sleep_time):
        self.sleep_time = sleep_time

    def eval(self):
        time.sleep(self.sleep_time)
        return "zzz"


def test_node():
    sleep_time = 0.5
    n = DizzyNode(sleep_time)
    n.eval()

    assert not hasattr(n, "benchmark")

    bm.patch_node(n)
    n.eval()

    assert hasattr(n, "benchmark")
    assert n.benchmark["eval_time"] >= sleep_time


def test_graph():
    sleep_time = 0.5
    x = Variable(name="input")
    c = Constant("lol")
    d = DizzyNode(sleep_time)

    g = Graph(x, d + c)
    g.run("this is ignored")

    assert not hasattr(g, "benchmark")

    bm.patch_graph(g)
    g.run("still ignored")

    assert hasattr(g, "benchmark")
    assert g.benchmark["run_time"] >= sleep_time
