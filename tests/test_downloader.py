import shutil
from glob import glob

import unittest

from pikax import AndroidAPIClient
from pikax import DefaultDownloader
from pikax import DefaultIDProcessor
from pikax import PikaxResult
from pikax import params
from pikax import settings


class DownloaderTest(unittest.TestCase):
    def test_download(self):
        client = AndroidAPIClient(settings.username, settings.password)
        processor = DefaultIDProcessor()
        downloader = DefaultDownloader()
        num_of_artworks = 7
        ids = client.rank(limit=num_of_artworks)
        self.assertEqual(len(ids), num_of_artworks)
        artworks, fails = processor.process(ids, process_type=params.ProcessType.ILLUST)
        self.assertEqual(len(artworks), num_of_artworks)
        result = PikaxResult(download_type=params.DownloadType.ILLUST, artworks=artworks)

        downloader.download(pikax_result=result, folder=settings.TEST_FOLDER)
        expected_pages = sum(len(artwork) for artwork in result.artworks)
        local_images = glob(settings.TEST_FOLDER + '/*.jpg') + glob(settings.TEST_FOLDER + '/*.png')
        self.assertEqual(len(local_images), expected_pages)
        shutil.rmtree(settings.TEST_FOLDER)

    # TODO: find a way to test for request exception when downloading


if __name__ == '__main__':
    unittest.main()
