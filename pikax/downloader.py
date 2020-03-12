import os
import re
from typing import Tuple, Iterator

import requests

from . import util
from .api.models import Artwork
from .models import BaseDownloader
from .texts import texts

__all__ = ['DefaultDownloader']


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
                artwork_detail = texts.ARTWORK_DETAIL_MESSAGE.format(title=artwork.title, page_num=page_num,
                                                                     author=artwork.author)
                if status is Artwork.DownloadStatus.OK:

                    if os.path.isfile(filename):
                        yield Artwork.DownloadStatus.SKIPPED, artwork_detail
                        continue

                    with requests.get(url=url, headers=headers) as req:
                        req.raise_for_status()
                        with open(filename, 'wb') as file:
                            for chunk in req.iter_content(chunk_size=1024):
                                file.write(chunk)
                    yield Artwork.DownloadStatus.OK, artwork_detail

                else:
                    yield Artwork.DownloadStatus.FAILED, artwork_detail

        except requests.RequestException as e:
            yield Artwork.DownloadStatus.FAILED, artwork_detail + f'{os.linesep}{e}'

    @staticmethod
    def download_manga(artwork: Artwork, folder: str = None) -> Iterator[Tuple[Artwork.DownloadStatus, str]]:
        return DefaultDownloader.download_illust(artwork=artwork, folder=folder)
