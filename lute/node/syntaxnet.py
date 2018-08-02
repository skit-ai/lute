import requests


class SyntaxNet(Node):
    """
    Syntaxnet node
    """

    def __init__(self, root_url: str):
        self.root_url = root_url

    def __call__(self, text: Node):
        text = text.encode('utf-8')
        self._register_predecessors([text])
        self._text_node = text

        return self

    def eval(self):
        req = requests.post(self.root_url, data={self._text_node.value}, headers={"Content-Type": "text/plain"})
        output = req.json()
        return output
