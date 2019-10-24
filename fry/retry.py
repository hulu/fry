import requests.packages.urllib3 as urllib3


class Refry(urllib3.Retry):

    def __init__(self, *args, **kwargs):
        super(Refry, self).__init__(*args, **kwargs)

    def _is_connection_error(self, err):
        """ Explicitly define errors we are okay to retry on
        """
        return isinstance(err, (urllib3.exceptions.ConnectionError, urllib3.exceptions.ConnectTimeoutError))
