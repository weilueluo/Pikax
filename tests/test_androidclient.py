import datetime

import unittest

from pikax import params, ClientException, APIUserError
from pikax import settings
from pikax.api.androidclient import AndroidAPIClient


class AndroidClientTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = AndroidAPIClient(settings.username, settings.password)
        self.user = self.client.visits(user_id=38088)

    def test_following(self):
        ids = self.client.followings(user_id=18526689, limit=10)
        self.assertEqual(len(ids), 10)

    def test_search(self):
        ids = self.client.search(keyword='arknights', limit=7)
        self.assertEqual(len(ids), 7)

    def test_bookmark(self):
        ids = self.client.bookmarks(limit=15)
        self.assertEqual(len(ids), 15)

    def test_manga(self):
        # TODO: add some mangas into the account
        ids = self.client.mangas(limit=0)
        self.assertEqual(len(ids), 0)

    def test_search2(self):
        ids = self.client.search(keyword='arknights', limit=23, sort=params.Sort.DATE_DESC,
                                 search_type=params.SearchType.ILLUST_OR_MANGA,
                                 match=params.Match.PARTIAL,
                                 search_range=params.Range.A_YEAR)
        self.assertEqual(len(ids), 23)

    def test_rank_rookie(self):
        ids = self.client.rank(rank_type=params.RankType.ROOKIE, date=datetime.date.today(),
                               content=params.Content.MANGA, limit=19)
        self.assertEqual(len(ids), 19)

    def test_user_illust(self):
        ids = self.user.illusts(limit=45)
        self.assertEqual(len(ids), 45)

    def test_user_manga(self):
        ids = self.user.mangas(limit=2)
        self.assertEqual(len(ids), 2)

    def test_following_invalid_id(self):
        with self.assertRaises(ClientException):
            self.client.followings(user_id=0, limit=123)

    def test_visits_invalid_id(self):
        with self.assertRaises(APIUserError):
            self.client.visits(user_id=0)

    def test_account(self):
        # default account's account name
        self.assertEqual(self.client.account, 'crawl_user')

    def test_name(self):
        # default account name is crawler
        self.assertEqual(self.client.name, 'crawler')

    def test_id(self):
        # default account's id
        self.assertEqual(self.client.id, '41689219')


if __name__ == '__main__':
    unittest.main()
