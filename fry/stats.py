class NullStatsClient(object):
    """This null stats client does nothing when called.
    """
    def increment(self, metric, delta=1):
        pass

    def histogram(self, metric, time):
        pass

    def get_timer(self):
        return NullTimer()


class NullTimer(object):
    def start(self):
        pass

    def stop(self, subname=""):
        pass
