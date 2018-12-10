import time

import lute.benchmark as bm
from lute.graph import Graph
from lute.node import Constant, Node, Variable


class DizzyNode(Node):
    def __init__(self, sleep_time):
        self.sleep_time = sleep_time

    def eval(self):
        time.sleep(self.sleep_time)
        return "zzz"


class DizzyInputNode(Node):
    def __init__(self, sleep_time):
        self.sleep_time = sleep_time

    def eval(self, inp: Node):
        time.sleep(self.sleep_time)
        return inp.value


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


def test_self_time():
    sleep_time = 0.2

    x = Variable(name="input")
    d1 = DizzyNode(sleep_time)
    d2 = DizzyNode(sleep_time)
    di1 = DizzyInputNode(sleep_time)
    di2 = DizzyInputNode(sleep_time)

    di1(x + d1)
    di2(di1 + d2)

    g = Graph(x, di2)

    bm.patch_graph(g)
    g.run("hehe")

    bm.calculate_self_time_graph(g)

    delta = sleep_time / 10
    assert sleep_time < d1.benchmark["eval_time"] < sleep_time + delta
    assert sleep_time < d1.benchmark["self_eval_time"] < sleep_time + delta

    assert sleep_time < d2.benchmark["eval_time"] < sleep_time + delta
    assert sleep_time < d2.benchmark["self_eval_time"] < sleep_time + delta

    assert 2 * sleep_time < di1.benchmark["eval_time"] < 2 * sleep_time + delta
    assert sleep_time < di1.benchmark["self_eval_time"] < sleep_time + delta

    assert 4 * sleep_time < di2.benchmark["eval_time"] < 4 * sleep_time + delta
    assert sleep_time < di2.benchmark["self_eval_time"] < sleep_time + delta
