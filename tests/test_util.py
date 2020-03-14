import unittest

from pikax import trim_to_limit, util, ReqException


class UtilTest(unittest.TestCase):
    def test_trim_to_limit(self):
        arr = range(243)
        new_arr = trim_to_limit(arr, 43)
        self.assertEqual(len(new_arr), 43)

        arr = range(231)
        new_arr = trim_to_limit(arr, 131)
        self.assertEqual(len(new_arr), 131)

    def test_req(self):
        # simple test, exhaustively tested in other tests anyway...
        # not good, maybe find better tests if have time
        url = 'https://www.google.com'
        self.assertEqual(util.req(url).status_code, 200)
        url = 'https://www.invalid.com'
        with self.assertRaises(ReqException):
            util.req(url)


if __name__ == '__main__':
    unittest.main()
