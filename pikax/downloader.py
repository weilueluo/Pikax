import os
import re
from typing import Tuple, Iterator

import requests

from .models import BaseDownloader
from . import util
from .api.models import Artwork


class DefaultDownloader(BaseDownloader):
    @staticmethod
    def download_illust(artwork: Artwork, folder: str = '') -> Iterator[Tuple[Artwork.DownloadStatus, str]]:
        artwork_detail = 'None'
        folder = str(folder)
        if folder and not os.path.isdir(folder):
            os.mkdir(folder)
        try:
            for status, url_and_headers, filename in artwork:
                url, headers = url_and_headers
                page_num_search = re.search(r'\d{8}_p(\d*)', url)
                page_num = page_num_search.group(1) if page_num_search else -1
                filename = os.path.join(util.clean_filename(str(folder)), util.clean_filename(str(filename)))
                artwork_detail = f'[{str(artwork.title)}] p{page_num} by [{str(artwork.author)}]'
                if status is Artwork.DownloadStatus.OK:

                    if os.path.isfile(filename):
                        yield Artwork.DownloadStatus.SKIPPED, artwork_detail
                        continue

                    with requests.get(url=url, headers=headers) as r:
                        r.raise_for_status()
                        with open(filename, 'wb') as file:
                            for chunk in r.iter_content(chunk_size=1024):
                                file.write(chunk)
                    yield Artwork.DownloadStatus.OK, artwork_detail

        except requests.RequestException as e:
            yield Artwork.DownloadStatus.FAILED, artwork_detail + f': {e}'

    @staticmethod
    def download_manga(artwork: Artwork, folder: str = None) -> Iterator[Tuple[Artwork.DownloadStatus, str]]:
        return DefaultDownloader.download_illust(artwork=artwork, folder=folder)


def test():
    from . import settings
    from .api.androidclient import AndroidAPIClient
    from pikax.processor import DefaultIDProcessor
    from . import params
    from .models import PikaxResult
    import shutil

    client = AndroidAPIClient(settings.username, settings.password)
    processor = DefaultIDProcessor()
    downloader = DefaultDownloader()
    num_of_artworks = 53
    ids = client.rank(limit=num_of_artworks)
    assert len(ids) == num_of_artworks, len(ids)
    artworks, fails = processor.process(ids, process_type=params.ProcessType.ILLUST)
    assert len(artworks) == num_of_artworks, len(artworks)
    result = PikaxResult(download_type=params.DownloadType.ILLUST, artworks=artworks)
    downloader.download(pikax_result=result, folder=settings.TEST_FOLDER)
    shutil.rmtree(settings.TEST_FOLDER)
    print(f'Removed test folder: {settings.TEST_FOLDER}')

    print('Successfully tested downloader')


def main():
    test()


if __name__ == '__main__':
    url = 'https://i.pximg.net/img-original/img/2019/11/23/20/19/39/77954646_p0.jpg'
    headers = {
        'referer': 'https://www.pixiv.net/'
    }
    filename = 'test_pic.jpg'
    with requests.get(url=url, headers=headers) as r:
        r.raise_for_status()
        with open(filename, 'wb') as file:
            for chunk in r.iter_content(chunk_size=1024):
                file.write(chunk)

    main()
