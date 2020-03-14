import unittest

from pikax import AndroidAPIClient, settings, Illust, ArtworkError


class ArtworkTest(unittest.TestCase):
    def test_artworks_from_user(self):
        client = AndroidAPIClient(settings.username, settings.password)
        user = client.visits(user_id=2957827)
        illust_ids = user.illusts(limit=13)
        artworks = [Illust(illust_id) for illust_id in illust_ids]
        for artwork in artworks:
            for status, (download_url, header), filename in artwork:
                self.assertTrue(status == artwork.DownloadStatus.OK)
                self.assertIsNotNone(download_url)
                self.assertIsNotNone(header)
                self.assertIsNotNone(filename)
            self.assertIsNotNone(artwork.id)
            self.assertIsNotNone(artwork.tags)
            self.assertIsNotNone(artwork.bookmarks)
            self.assertIsNotNone(artwork.likes)
            self.assertIsNotNone(artwork.title)
            self.assertEqual(artwork.author, user.name)

    def test_invalid_artwork(self):
        with self.assertRaises(ArtworkError):
            _ = Illust(-123)


if __name__ == '__main__':
    unittest.main()
