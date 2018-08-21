
class TypeMismatchException(Exception):

    def __init__(self, expected_type, got_type, *args, **kwargs):
        message = "Type Mismatch: Expected %s got %s" % (expected_type, got_type)
        super().__init__(message, *args, **kwargs)


class ResolutionException(Exception):
    """
    Exception for resolving a node from a list
    """

    def __init__(self, node_id, *args, **kwargs):
        message = f"Unable to resolve {node_id}"
        super().__init__(message, *args, **kwargs)
