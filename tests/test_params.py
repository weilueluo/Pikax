import unittest

from pikax.params import *


class ParamsTest(unittest.TestCase):
    def test_type(self):
        self.assertTrue(Type.is_valid(Type.ILLUST))
        self.assertTrue(Type.is_valid(Type.USER))
        self.assertTrue(Type.is_valid(Type.MANGA))

        self.assertFalse(Type.is_valid(Match.EXACT))
        self.assertFalse(Type.is_valid(Sort.DATE_DESC))
        self.assertFalse(Type.is_valid(Date.TODAY))

    def test_match(self):
        self.assertTrue(Match.is_valid(Match.EXACT))
        self.assertTrue(Match.is_valid(Match.ANY))
        self.assertTrue(Match.is_valid(Match.PARTIAL))

        self.assertFalse(Match.is_valid(Dimension.HORIZONTAL))
        self.assertFalse(Match.is_valid(Range.A_WEEK))
        self.assertFalse(Match.is_valid(RankType.ROOKIE))

    def test_rank_type(self):
        self.assertTrue(RankType.is_valid(RankType.ROOKIE))
        self.assertTrue(RankType.is_valid(RankType.MONTHLY))
        self.assertTrue(RankType.is_valid(RankType.DAILY))
        self.assertTrue(RankType.is_valid(RankType.WEEKLY))

        self.assertFalse(RankType.is_valid(Dimension.HORIZONTAL))
        self.assertFalse(RankType.is_valid(Range.A_WEEK))
        self.assertFalse(RankType.is_valid(Date.TODAY))

    def test_sort(self):
        self.assertTrue(Sort.is_valid(Sort.DATE_DESC))
        self.assertTrue(Sort.is_valid(Sort.DATE_ASC))

        self.assertFalse(Sort.is_valid(Dimension.HORIZONTAL))
        self.assertFalse(Sort.is_valid(Range.A_WEEK))
        self.assertFalse(Sort.is_valid(Date.TODAY))


if __name__ == '__main__':
    unittest.main()
