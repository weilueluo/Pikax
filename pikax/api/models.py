import datetime
import enum
import functools
import os
from multiprocessing.dummy import Pool
from typing import List, Tuple, Union, Type, Any
from .. import params, util
from ..exceptions import ArtworkError


class APIUserInterface:

    def bookmarks(self, limit: int = None, bookmark_type: params.BookmarkType = params.BookmarkType.ILLUST_OR_MANGA,
                  restrict: params.Restrict = params.Restrict.PUBLIC) -> List[int]:
        raise NotImplementedError

    def illusts(self, limit: int = None) -> List[int]: raise NotImplementedError

    def novels(self, limit: int = None) -> List[int]:
        raise NotImplementedError

    def mangas(self, limit: int = None) -> List[int]: raise NotImplementedError


class APIAccessInterface:
    def visits(self, user_id: int) -> APIUserInterface:
        raise NotImplementedError


class APIPagesInterface:

    def search(self, keyword: str = '',
               type: params.Type = params.Type.ILLUST,
               match: params.Match = params.Match.PARTIAL,
               sort: params.Sort = params.Sort.DATE_DESC,
               range: Union[datetime.timedelta, params.Range] = None,
               limit: int = None) -> List[int]: raise NotImplementedError

    def rank(self,
             limit: int = None,
             date: Union[str, datetime.date] = format(datetime.date.today(), '%Y%m%d'),
             content: params.Content = params.Content.ILLUST,
             type: params.Rank = params.Rank.DAILY) -> List[int]: raise NotImplementedError


class Artwork:

    def __init__(self, artwork_id):
        self.id = artwork_id

    @property
    def bookmarks(self): raise NotImplementedError

    @property
    def views(self): raise NotImplementedError

    @property
    def author(self): raise NotImplementedError

    @property
    def title(self): raise NotImplementedError

    @property
    def likes(self): raise NotImplementedError

    class DownloadStatus(enum.Enum):
        OK = '[OK]'
        SKIPPED = '[skipped]'
        FAILED = '<failed>'

    # return download status, content, filename
    def __getitem__(self, index) -> Tuple[DownloadStatus, Any, str]: raise NotImplementedError

    # return num of pages
    def __len__(self): raise NotImplementedError

    # set variables, raises ReqException if fails
    def config(self):
        raise NotImplementedError


class BaseIDProcessor:

    def __init__(self):
        self.type_to_function = {
            params.ProcessType.NOVEL: self.process_novels,
            params.ProcessType.MANGA: self.process_mangas,
            params.ProcessType.ILLUST: self.process_illusts,
            params.ProcessType.GIF: self.process_gifs
        }

    def process_illusts(self, ids: List[int]) -> Tuple[List[Artwork], List[int]]:
        raise NotImplementedError

    def process_novels(self, ids: List[int]) -> Tuple[List[Artwork], List[int]]:
        raise NotImplementedError

    def process_gifs(self, ids: List[int]) -> Tuple[List[Artwork], List[int]]:
        raise NotImplementedError

    def process_mangas(self, ids: List[int]) -> Tuple[List[Artwork], List[int]]:
        raise NotImplementedError

    def process(self, ids: List[int], process_type: params.ProcessType) -> Tuple[List[Artwork], List[int]]:
        if process_type not in [params.ProcessType.ILLUST, params.ProcessType.NOVEL, params.ProcessType.MANGA,
                                params.ProcessType.GIF]:
            from ..exceptions import ProcessError
            raise ProcessError(f'Invalid process type: {process_type}, should be in '
                               f'{[params.ProcessType.ILLUST, params.ProcessType.NOVEL, params.ProcessType.MANGA, params.ProcessType.GIF]}')

        return self.type_to_function[process_type](ids)

    @staticmethod  # param cls is pass in as argument
    def _general_processor(cls: Type[Artwork], item_ids: List[int]) -> Tuple[List[Artwork], List[int]]:
        successes = []
        fails = []

        for item_id in item_ids:
            try:
                successes.append(cls(item_id))
            except ArtworkError:
                fails.append(item_id)

        return successes, fails


class BaseDownloader:

    @staticmethod
    def download_illust(artwork: Artwork, folder: str = None) -> Tuple[Artwork.DownloadStatus, str]:
        raise NotImplementedError

    @staticmethod
    def download_novel(artwork: Artwork, folder: str = None) -> Tuple[Artwork.DownloadStatus, str]:
        raise NotImplementedError

    @staticmethod
    def download_gif(artwork: Artwork, folder: str = None) -> Tuple[Artwork.DownloadStatus, str]:
        raise NotImplementedError

    @staticmethod
    def download_manga(artwork: Artwork, folder: str = None) -> Tuple[Artwork.DownloadStatus, str]:
        raise NotImplementedError

    def __init__(self):
        self.download_type_to_function = {
            params.DownloadType.ILLUST: self.download_illust,
            params.DownloadType.NOVEL: self.download_novel,
            params.DownloadType.MANGA: self.download_manga,
            params.DownloadType.GIF: self.download_gif
        }

    @staticmethod
    def config_artworks(artworks: List[Artwork]):
        util.log('Configuring artworks', start=os.linesep, inform=True)
        total = len(artworks)
        config_artworks = []
        failed_config_artworks = dict()  # reason map to artwork
        pool = Pool()

        def config_artwork(item):
            try:
                item.config()
                config_artworks.append(item)
            except ArtworkError as e:
                failed_config_artworks[str(e)] = item

        for index, _ in enumerate(pool.imap_unordered(config_artwork, artworks)):
            util.print_progress(index + 1, total)
        util.print_done()

        if failed_config_artworks:
            for reason, failed_artwork in failed_config_artworks.items():
                util.log(f'Artwork with id: {failed_artwork.id} failed config for download: {reason}', error=True)

        util.log(f'expected: {total}', inform=True)
        util.log(f'success: {len(config_artworks)}', inform=True)
        util.log(f'failed: {len(failed_config_artworks)}', inform=True)

        return config_artworks

    def download(self, download_type: params.DownloadType, artworks: List[Artwork], folder: str = ''):

        folder = util.clean_filename(folder)
        if not os.path.isdir(folder):
            os.mkdir(folder)

        download_function = self.download_type_to_function[download_type]
        download_function = functools.partial(download_function, folder=folder)
        artworks = self.config_artworks(artworks)
        successes = []
        fails = []
        skips = []
        total = len(artworks)
        pool = Pool()
        util.log('Downloading Artworks', start=os.linesep, inform=True)

        for index, download_details in enumerate(pool.imap_unordered(download_function, artworks)):
            status, msg = download_details
            info = str(msg) + ' ' + str(status.value)
            if status is Artwork.DownloadStatus.OK:
                successes.append(msg)
            elif status is Artwork.DownloadStatus.SKIPPED:
                skips.append(msg)
            else:
                fails.append(msg)
            util.print_progress(index + 1, total, msg=info)
        util.print_done()

        util.log(f'There are {len(successes)} downloaded artworks', inform=True)

        util.log(f'There are {len(skips)} skipped artworks', inform=True)
        for index, skip_info in enumerate(skips):
            util.log(skip_info, start=f' [{index + 1}]: ', inform=True)

        util.log(f'There are {len(fails)} failed artworks', inform=True)
        for index, skip_info in enumerate(fails):
            util.log(skip_info, start=f' [{index + 1}]: ', inform=True)

        util.print_done(str(folder))
