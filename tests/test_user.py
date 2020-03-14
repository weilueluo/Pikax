import unittest

from pikax import AndroidAPIClient, settings, DefaultPikaxUser


class UserTest(unittest.TestCase):
    def setUp(self) -> None:
        client = AndroidAPIClient(settings.username, settings.password)
        self.user = DefaultPikaxUser(client, user_id=14112962)

    def test_illust(self):
        illusts = self.user.illusts(limit=34)
        self.assertEqual(len(illusts), 34)

    def test_bookmarks(self):
        bookmarks = self.user.bookmarks(limit=23)
        self.assertEqual(len(bookmarks), 23)

    def test_mangas(self):
        mangas = self.user.illusts(limit=2)
        self.assertEqual(len(mangas), 2)


if __name__ == '__main__':
    unittest.main()
