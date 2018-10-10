"""
Logging facility for graphs.
"""

import json
import os
import time
from typing import Any, Callable

from pydash import py_

from lute.graph import Graph

Logger = Callable[[Graph], Any]

print_logger: Logger = py_.flow_right(lambda g: g.to_dict(), print)


def make_json_logger(f: str):
    def _logger(g):
        if os.path.exists(f):
            with open(f) as fp:
                items = json.load(fp)
        else:
            items = []

        items.append({
            "time": time.time(),
            "value": g.to_dict()
        })

        with open(f, "w") as fp:
            json.dump(items, fp)

    return _logger
