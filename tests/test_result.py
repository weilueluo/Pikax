import unittest

from pikax import Pikax, settings, PikaxResult


class ResultTest(unittest.TestCase):
    def setUp(self) -> None:
        self.pikax = Pikax(settings.username, settings.password)
        self.result1 = self.pikax.rank(25)
        self.result2 = self.pikax.search('arknights', limit=10)

    def test_result(self):
        self.assertIsNotNone(self.result2.artworks)
        self.assertIsNotNone(self.result1.artworks)

    def test_operator(self):
        # this method does not check if it is correct, only check if it works without error
        result = self.result2.likes > 10
        self.assertIsInstance(result, PikaxResult)
        result = self.result1.likes < 20
        self.assertIsInstance(result, PikaxResult)
        result = self.result1.likes <= 12
        self.assertIsInstance(result, PikaxResult)
        result = self.result1.likes >= 7
        self.assertIsInstance(result, PikaxResult)
        result = self.result2.likes != 0
        self.assertIsInstance(result, PikaxResult)
        result = self.result1.likes == 5
        self.assertIsInstance(result, PikaxResult)

        result = self.result1.bookmarks >= 5
        self.assertIsInstance(result, PikaxResult)

        result = self.result1.bookmarks > 123
        self.assertIsInstance(result, PikaxResult)

        result = self.result1.views < 123456
        self.assertIsInstance(result, PikaxResult)

        result = self.result2.views != 567587
        self.assertIsInstance(result, PikaxResult)

    def test_result_add(self):
        sum_result = self.result1 + self.result2
        self.assertEqual(len(sum_result), 25 + 10)

    def test_result_sub(self):
        sub_result = self.result1 - self.result2
        self.assertEqual(len(sub_result), 25)


if __name__ == '__main__':
    unittest.main()
