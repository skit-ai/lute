
class TypeMismatchException(Exception):

    def __init__(self, expected_type, got_type, *args, **kwargs):
        message = "Type Mismatch: Expected %s got %s" % (expected_type, got_type)
        super().__init__(message, *args, **kwargs)
