import os
from typing import Tuple

import requests

from pikax.api.models import Artwork
from .models import BaseDownloader
from .. import util


class DefaultDownloader(BaseDownloader):
    @staticmethod
    def download_illust(artwork: Artwork, folder: str = None) -> Tuple[Artwork.DownloadStatus, str]:
        artwork_detail = 'None'
        try:
            for status, url_and_headers, filename in artwork:
                url, headers = url_and_headers
                filename = util.clean_filename(os.path.join(str(folder), str(filename)))
                artwork_detail = '[' + str(artwork.title) + '] by [' + str(artwork.author) + ']'
                if status is Artwork.DownloadStatus.OK:

                    if os.path.isfile(filename):
                        return Artwork.DownloadStatus.SKIPPED, artwork_detail

                    with requests.get(url=url, headers=headers, stream=True) as r:
                        r.raise_for_status()
                        with open(filename, 'wb') as file:
                            for chunk in r.iter_content(chunk_size=1024):
                                file.write(chunk)

                    return Artwork.DownloadStatus.OK, artwork_detail

        except requests.RequestException as e:
            return Artwork.DownloadStatus.FAILED, artwork_detail

    @staticmethod
    def download_novel(artwork: Artwork, folder: str = None) -> Tuple[Artwork.DownloadStatus, str]:
        pass

    @staticmethod
    def download_gif(artwork: Artwork, folder: str = None) -> Tuple[Artwork.DownloadStatus, str]:
        pass

    @staticmethod
    def download_manga(artwork: Artwork, folder: str = None) -> Tuple[Artwork.DownloadStatus, str]:
        pass


def test():
    from .. import settings
    from ..api.androidclient import AndroidAPIClient
    from ..api.processor import DefaultIDProcessor
    from .. import params

    client = AndroidAPIClient(settings.username, settings.password)
    processor = DefaultIDProcessor()
    downloader = DefaultDownloader()

    ids = client.rank(limit=123)
    print(f'ids found: {len(ids)}')
    artworks, fails = processor.process(ids, process_type=params.ProcessType.ILLUST)
    print(f'success: {len(artworks)}, fails: {len(fails)}')
    downloader.download(artworks=artworks, download_type=params.DownloadType.ILLUST, folder='#test_download')


def main():
    test()


if __name__ == '__main__':
    main()
