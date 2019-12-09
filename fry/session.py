import time

import requests
import requests.adapters as adapters
import requests.packages.urllib3 as urllib3

from fry.retry import Refry
from fry import stats


DEFAULT_TIMEOUT = 5


class FrySession(requests.Session):

    def __init__(self, stats_client=None, adapter_settings=None):
        """FrySession constructor

        Here we set the stats_client to be used and parse out the adapter_settings

        Args:
            stats_client (DogStatsd, optional): DogStatsd object for FrySession to send stats through
            adapter_settings (dict, optional): Dictionary of adapter settings for session. Adapter settings and retry
                settings are standard for requests library.
        """
        super(FrySession, self).__init__()

        self.stats_client = stats_client if stats_client else stats.NullStatsd()
        self.adapter_settings = adapter_settings if adapter_settings else {}

        self._build_adapters()

    def _build_adapters(self):
        """Parse adapter_settings to build adapters and mount within this session

        If retry settings are included, a retry object is built for the adapter.
        """
        for prefix, settings in self.adapter_settings.items():
            adapter = adapters.HTTPAdapter()

            if 'adapter' in settings:
                if 'retry' in settings:
                    adapter = adapters.HTTPAdapter(
                        max_retries=Refry(**settings['retry']),
                        **settings['adapter']
                    )
                else:
                    adapter = adapters.HTTPAdapter(**settings['adapter'])

            adapter.config.update(settings.get('adapter_config', {}))

            self.mount(prefix, adapter)

    """Request methods"""

    def make_request(self, method, url, signature, **kwargs):
        """Make a tracked request using the requests library and class stats client

        Note that because FrySession is intended to be used across many dependencies, any session cookies are cleared
        before making a request so as not to change the response in an unintended way. Cookies can still be passed via
        the `cookie` kwarg.

        Args:
            method: HTTP method to use for request
            url: url to make the request against
            signature: Stats signature for this request (ex: {service}.{endpoint})
            **kwargs: Any requests (library) kwargs to be passed along (i.e. data, headers, etc)

        Returns:
            requests.Response
        """

        request_retries = 0
        request_adapter = self.get_adapter(url)
        adapter_retries = getattr(request_adapter, 'max_retries', urllib3.Retry(0)).total
        timeout = getattr(request_adapter, 'config', {}).get('timeout', DEFAULT_TIMEOUT)

        self.cookies.clear()

        try:
            response = self._perform_timed_request(method, url, timeout, signature, **kwargs)
            self._track_status_code(signature, response.status_code)
            request_retries = adapter_retries - response.raw.retries.total
            return response
        except Exception as ex:
            # assume that all retries were exercised on a raised ConnectionError or Timeout
            if isinstance(ex, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)):
                request_retries = adapter_retries

            # Track the error as a 500 in the status code stats
            self._track_status_code(signature, 500)
            self._track_error(signature, ex)
            raise
        finally:
            self._track_retries(signature, request_retries)

    def _perform_timed_request(self, method, url, timeout, signature, **kwargs):
        """Performs request and reports timing stats using class stats client

        Args:
            method: HTTP method to use for request
            url: url to make the request against
            timeout: timeout for request
            signature: Stats signature for this request (ex: {service}.{endpoint})
            **kwargs: Any requests (library) kwargs to be passed along (i.e. data, headers, etc)

        Returns:
            requests.Response
        """
        start = time.time()

        try:
            response = self.request(method, url, timeout=timeout, **kwargs)
        finally:
            stat = "ResponseTimeByBackend.{0}".format(signature)
            self.stats_client.timing(stat, time.time() - start)

        return response

    """Stats tracking methods"""

    def _track_error(self, signature, ex):
        stat = "ErrorByBackend.{0}".format(signature)
        type_tag = "type:{0}".format(ex.__class__.__name__)
        self.stats_client.increment(stat, value=1, tags=[type_tag])

    def _track_retries(self, signature, retries):
        stat = "RetriesByBackend.{0}".format(signature)
        self.stats_client.histogram(stat, value=int(retries))

    def _track_status_code(self, signature, status_code):
        stat = "StatusCodeByBackend.{0}".format(signature)
        status_code_tag = "status_code:{0}".format(status_code)
        self.stats_client.increment(stat, value=1, tags=[status_code_tag])
