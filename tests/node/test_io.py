from lute.graph import Graph
from lute.node import Variable
from lute.node.io import IORead, IOWrite


def write_file(file_obj, data):
    for item in data:
        file_obj.write(str(item) + '\n')


def read_file(file_obj):
    return file_obj.read().splitlines()


def test_write_file():
    v = Variable()
    file_path = "tests/data/test_io_write.txt"
    g = Graph(v, v >> IOWrite(file_path, write_file))

    assert file_path == g.run(["cat", "dog"])


def test_read_file():
    v = Variable()
    g = Graph(v, v >> IORead(read_file))

    assert ["hello", "how", "are", "you"] == g.run("tests/data/test_io_read.txt")
