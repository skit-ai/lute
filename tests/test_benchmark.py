import time

import lute.benchmark as bm
from lute.graph import Graph
from lute.node import Constant, Identity, Node, Variable


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

    assert not bm.node_has_benchmark(n)

    bm.patch_node(n)
    n.eval()

    assert bm.node_has_benchmark(n)
    assert len(n.benchmark["eval_times"]) == 1
    assert n.benchmark["eval_times"][-1] >= sleep_time


def test_node_store():
    n = Constant(1)
    store_size = 2
    bm.patch_node(n, store_size=store_size)

    n.eval()
    assert len(n.benchmark["eval_times"]) == 1
    assert len(n.benchmark["self_eval_times"]) == 1

    for _ in range(store_size * 2):
        n.eval()

    assert len(n.benchmark["eval_times"]) == store_size
    assert len(n.benchmark["self_eval_times"]) == store_size


def test_graph():
    sleep_time = 0.5
    x = Variable(name="input")
    c = Constant("lol")
    d = DizzyNode(sleep_time)

    g = Graph(x, d + c)
    g.run("this is ignored")

    assert not bm.graph_has_benchmark(g)

    bm.patch_graph(g)
    g.run("still ignored")

    assert bm.graph_has_benchmark(g)
    assert len(g.benchmark["run_times"]) == 1
    assert g.benchmark["run_times"][-1] >= sleep_time


def test_graph_multiple_run():
    sleep_time = 0.1
    x = Variable(name="input")
    c = Constant("lol")
    d = DizzyNode(sleep_time)

    g = Graph(x, d + c)
    g.run("this is ignored")

    assert not bm.graph_has_benchmark(g)

    bm.patch_graph(g)
    g.run("still ignored")
    g.run("not really")

    assert bm.graph_has_benchmark(g)
    assert len(g.benchmark["run_times"]) == 2


def test_graph_store():
    store_size = 3
    x = Variable(name="input")
    i = Identity()(x)

    g = Graph(x, i)
    bm.patch_graph(g, store_size)
    g.run("something")

    assert len(g.benchmark["run_times"]) == 1
    for n in g._nodes:
        assert len(n.benchmark["eval_times"]) == 1

    for _ in range(store_size * 2):
        g.run("something")

    assert len(g.benchmark["run_times"]) == store_size
    for n in g._nodes:
        assert len(n.benchmark["eval_times"]) == store_size


def test_self_time():
    sleep_time = 0.2

    x = Variable(name="input")
    d1 = DizzyNode(sleep_time)
    d2 = DizzyNode(sleep_time)
    di1 = DizzyInputNode(sleep_time)
    di2 = DizzyInputNode(sleep_time)
    di3 = DizzyInputNode(sleep_time)

    di1(x + d1)
    di2(di1 + d2)
    di3(d2)

    out = di2 + d2 + di3
    g = Graph(x, out)

    bm.patch_graph(g)
    g.run("hehe")

    delta = sleep_time / 10
    assert sleep_time < d1.benchmark["eval_times"][-1] < sleep_time + delta
    assert sleep_time < d1.benchmark["self_eval_times"][-1] < sleep_time + delta

    assert sleep_time < d2.benchmark["eval_times"][-1] < sleep_time + delta
    assert sleep_time < d2.benchmark["self_eval_times"][-1] < sleep_time + delta

    assert 2 * sleep_time < di1.benchmark["eval_times"][-1] < 2 * sleep_time + delta
    assert sleep_time < di1.benchmark["self_eval_times"][-1] < sleep_time + delta

    assert 4 * sleep_time < di2.benchmark["eval_times"][-1] < 4 * sleep_time + delta
    assert sleep_time < di2.benchmark["self_eval_times"][-1] < sleep_time + delta

    assert sleep_time < di3.benchmark["eval_times"][-1] < sleep_time + delta
    assert sleep_time < di3.benchmark["self_eval_times"][-1] < sleep_time + delta

    assert 5 * sleep_time < out.benchmark["eval_times"][-1] < 5 * sleep_time + delta
    assert 0 < out.benchmark["self_eval_times"][-1] < delta

    assert 5 * sleep_time < g.benchmark["run_times"][-1] < 5 * sleep_time + delta
