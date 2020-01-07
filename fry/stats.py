from functools import wraps


class NullStatsd(object):
    """This null stats client does nothing when called.
    """
    def increment(self, *args, **kwargs):
        pass

    def histogram(self, *args, **kwargs):
        pass

    def timing(self, *args, **kwargs):
        pass
