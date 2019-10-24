import requests
import requests.cookies
import requests.packages.urllib3 as urllib3

import httmock
import unittest

from fry import FrySession


@httmock.all_requests
def http_mock(_, request):
    response = requests.Response()
    response.raw = urllib3.response.HTTPResponse(retries=urllib3.Retry(total=1))
    response.status_code = 200
    response.url = request.url

    if 'example.com/endpoint' in request.url:
        # return the post body as the response content
        response._content = request.body
    elif 'example.com/set_cookie' in request.url:
        # return a cookie in the response
        response.cookies = requests.cookies.cookiejar_from_dict({'cookie': 'one'})
    elif 'example.com/get_num_cookies' in request.url:
        # return the number of cookies in the request as the response content
        response._content = len(request._cookies.items())
    return response


class TestFrySession(unittest.TestCase):

    def setUp(self):
        self.adapter_settings = {
            'http://www.example.com': {
                'retry': {
                    'total': 3,
                    'read': 3,
                    'connect': 3
                },
                'adapter': {
                    'pool_maxsize': 4,
                },
                'adapter_config': {
                    'timeout': 0.5
                }
            }
        }

    def test_init_empty_settings(self):
        fsession = FrySession()

        self.assertEqual(len(fsession.adapters), 2, "Should only have default two adapters")

    def test_init_with_settings(self):
        fsession = FrySession(stats_client=None, adapter_settings=self.adapter_settings)
        self.assertEqual(len(fsession.adapters), 3, "Should have base two adapters plus new one")

        example_adapter = fsession.get_adapter('http://www.example.com')
        self.assertEqual(getattr(example_adapter, 'max_retries').total, 3,
                         "example adapter retries should match adapter_settings")
        self.assertEqual(getattr(example_adapter, '_pool_maxsize'), 4,
                         "example adapter pool should match adapter_settings")
        self.assertEqual(getattr(example_adapter, 'config').get('timeout'), 0.5,
                         "example adapter should have timeout defined in its config")

    def test_make_get_request(self):
        fsession = FrySession(stats_client=None, adapter_settings=self.adapter_settings)

        url = 'http://www.example.com/endpoint'
        request_params = {'paul': "rules"}

        with httmock.HTTMock(http_mock):
            response = fsession.make_request('GET', url, 'Example.example', params=request_params)
        self.assertIn("paul=rules", response.url)

    def test_make_post_request(self):
        fsession = FrySession(stats_client=None, adapter_settings=self.adapter_settings)

        url = 'http://www.example.com/endpoint'
        request_data = {'paul': "rules"}

        with httmock.HTTMock(http_mock):
            response = fsession.make_request('GET', url, 'Example.example', data=request_data)

        self.assertIn("paul=rules", response.content)

    def test_no_cookie_persistence(self):
        fsession = FrySession(stats_client=None, adapter_settings=self.adapter_settings)

        with httmock.HTTMock(http_mock):
            fsession.make_request('GET', 'http://www.example.com/set_cookies', 'Example.example')
            response = fsession.make_request('GET', 'http://www.example.com/get_num_cookies', 'Example.example')

        self.assertEqual(0, int(response.content))

    def test_cookie_via_args(self):
        fsession = FrySession(stats_client=None, adapter_settings=self.adapter_settings)

        with httmock.HTTMock(http_mock):
            response = fsession.make_request('GET', 'http://www.example.com/get_num_cookies',
                                             'Example.example', cookies={'cookie': 'one'})

        self.assertEqual(1, int(response.content))


if __name__ == "__main__":
    unittest.main()
