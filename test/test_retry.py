import unittest
import requests.packages.urllib3 as urllib3

from fry.retry import Refry


class TestRefry(unittest.TestCase):

    def test_is_connection_error(self):
        refry = Refry()

        self.assertTrue(refry._is_connection_error(urllib3.exceptions.ConnectionError()))
        self.assertTrue(refry._is_connection_error(urllib3.exceptions.ConnectTimeoutError()))

if __name__ == "__main__":
    unittest.main()
