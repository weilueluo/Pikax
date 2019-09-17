import datetime
import functools
import math
import operator
import os
from multiprocessing.dummy import Pool
from typing import Union, List, Tuple, Iterator

from . import params, settings, util
from .api.models import Artwork


class PikaxResult:
    """
    This is the interface for result return by operation such as search, rank or result.likes > 1000 etc...
    """

    def __init__(self, artworks: List[Artwork], download_type: params.DownloadType, folder: str = ''):
        if any(not issubclass(artwork.__class__, Artwork) for artwork in artworks):
            from .exceptions import PikaxResultError
            raise PikaxResultError(f'artworks must all be subclass of {Artwork}')

        self._artworks = artworks
        self._folder = str(folder)
        self._download_type = download_type
        maker = functools.partial(self.result_maker, download_type=download_type)
        self._likes = self.ComparableItem(self, maker, 'likes')
        self._bookmarks = self.ComparableItem(self, maker, 'bookmarks')
        self._views = self.ComparableItem(self, maker, 'views')

    def result_maker(self, artworks, download_type, folder):
        raise NotImplemented

    def __add__(self, other: 'PikaxResult') -> 'PikaxResult':
        """
        This provide implementation of + of PikaxResult which result in a PikaxResult
        returned after adding artworks in both result
        :param other: the other PikaxResult, they must have same DownloadType
        :rtype: PikaxResult
        """
        raise NotImplementedError

    def __sub__(self, other: 'PikaxResult') -> 'PikaxResult':
        """
        This provide implementation of - of PikaxResult which result in a PikaxResult
        contains all artworks in the self which are not in other
        :rtype: PikaxResult
        """
        raise NotImplementedError

    def __getitem__(self, index: int) -> Artwork:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    @property
    def artworks(self):
        return self._artworks

    @property
    def folder(self):
        return self._folder

    class ComparableItem:
        _operator_to_symbol = {
            operator.eq: '==',
            operator.ne: '!=',
            operator.gt: '>',
            operator.lt: '<',
            operator.ge: '>=',
            operator.le: '<=',
        }

        _operator_to_name = {
            operator.eq: 'eq',
            operator.ne: 'ne',
            operator.gt: 'gt',
            operator.lt: 'lt',
            operator.ge: 'ge',
            operator.le: 'le',
        }

        def __init__(self, outer_self, result_maker, name):
            self.name = name
            self.outer_self = outer_self
            self.result_maker = result_maker

        def __eq__(self, value):
            return self._compare(operator.eq, value)

        def __ne__(self, value):
            return self._compare(operator.ne, value)

        def __gt__(self, value):
            return self._compare(operator.gt, value)

        def __ge__(self, value):
            return self._compare(operator.ge, value)

        def __lt__(self, value):
            return self._compare(operator.lt, value)

        def __le__(self, value):
            return self._compare(operator.le, value)

        def _compare(self, compare_operator, value):
            operator_symbol = self._operator_to_symbol[compare_operator]
            util.log(f'Filtering {self.name} {operator_symbol} {value}', start=os.linesep, inform=True)

            old_len = len(self.outer_self.artworks)
            new_artworks = list(
                filter(lambda item: compare_operator(getattr(item, self.name), value), self.outer_self.artworks))
            new_len = len(new_artworks)

            operator_name = self._operator_to_name[compare_operator]
            folder = util.clean_filename(str(self.outer_self.folder) + '_' + operator_name + '_' + str(value))
            result = self.result_maker(artworks=new_artworks, folder=folder)

            util.log(f'[ done ] {old_len} => {new_len}', inform=True)
            return result

    @property
    def likes(self) -> ComparableItem:
        return self._likes

    @property
    def views(self) -> ComparableItem:
        return self._views

    @property
    def bookmarks(self) -> ComparableItem:
        return self._bookmarks

    @property
    def download_type(self) -> params.DownloadType:
        return self._download_type


class PikaxUserInterface:
    """
    This is the interface of user returned in Pikax operation such as Pikax.visits
    """

    def illusts(self, limit: int = None) -> PikaxResult:
        """
        Return the illustrations uploaded by this user on Pixiv
        :param limit: Number of illustrations to return
        :rtype: PikaxResult
        """
        raise NotImplementedError

    def mangas(self, limit: int = None) -> PikaxResult:
        """
        Return the mangas uploaded by this user on Pixiv
        :param limit: Number of mangas to return
        :rtype: PikaxResult
        """
        raise NotImplementedError

    def bookmarks(self, limit: int = None,
                  bookmark_type: params.BookmarkType = params.BookmarkType.ILLUST_OR_MANGA) -> PikaxResult:
        """
        Return the bookmarks saved by this user on Pixiv
        :param bookmark_type: The rank_type of bookmark to return, must be enum of params.BookmarkType
        :param limit: Number of mangas to return
        :rtype: PikaxResult
        """
        raise NotImplementedError

    @property
    def id(self) -> int:
        """
        The id of this user in Pixiv
        :rtype: int
        """
        raise NotImplementedError

    @property
    def name(self) -> str:
        """
        The user name of this user on Pixiv
        :rtype: str
        """
        raise NotImplementedError

    @property
    def account(self) -> str:
        """
        The account name of this user on Pixiv
        :rtype: str
        """
        raise NotImplementedError


class PikaxPagesInterface:
    """
    The methods to implement if the subclass support pages operations
    """

    def search(self, keyword: str = '',
               search_type: params.Type = params.Type.ILLUST,
               match: params.Match = params.Match.PARTIAL,
               sort: params.Sort = None,
               search_range: datetime.timedelta = None,
               popularity: int = None,
               limit: int = None) \
            -> PikaxResult:
        """

        Perform search on Pixiv and returns the results

        :param keyword: the word to search
        :param search_type: rank_type of artwork to search
        :param match: define how strict the keywords are matched against artworks
        :param sort: order of the search result
        :param search_range: the date offset from today, can be a datetime.timedelta object
        :param popularity: if given, {popularity}users入り will be added after keywords
        :param limit: return number of artwork specified by limit, all by default
        :return: an object implement PikaxResult
        :rtype: PikaxResult
        """
        raise NotImplementedError

    def rank(self,
             limit: int = None,
             date: Union[str, datetime.datetime] = format(datetime.datetime.today(), '%Y%m%d'),
             content: params.Content = params.Content.ILLUST,
             rank_type: params.RankType = params.RankType.DAILY) \
            -> PikaxResult:
        """

        Retrieve ranking's artworks from Pixiv

        :param limit: the number of artworks to return
        :param date: the date of ranking
        :param content: the rank_type of artwork to rank
        :param rank_type: the mode for ranking, daily, monthly etc ...
        :return: an object implement PikaxResult
        :rtype: PikaxResult
        """
        raise NotImplementedError


class PikaxInterface(PikaxPagesInterface):
    """
    The api entry interface
    """

    def search(self, keyword: str = '', search_type: params.SearchType = params.SearchType.ILLUST_OR_MANGA,
               match: params.Match = params.Match.PARTIAL, sort: params.Sort = None, popularity: int = None,
               search_range: datetime.timedelta = None, limit: int = None) -> PikaxResult:
        """

        Perform search on Pixiv and returns the results

        :param keyword: the word to search
        :param search_type: rank_type of artwork to search
        :param match: define how strict the keywords are matched against artworks
        :param sort: order of the search result
        :param search_range: the date offset from today, can be a datetime.timedelta object
        :param popularity: if given, {popularity}users入り will be added after keywords
        :param limit: return number of artwork specified by limit, all by default
        :return: an object implement PikaxResult
        :rtype: PikaxResult
        """
        raise NotImplementedError

    def rank(self, limit: int = None, date: Union[str, datetime.datetime] = format(datetime.datetime.today(), '%Y%m%d'),
             content: params.Content = params.Content.ILLUST,
             rank_type: params.RankType = params.RankType.DAILY) -> PikaxResult:
        """

        Retrieve ranking's artworks from Pixiv

        :param limit: the number of artworks to return
        :param date: the date of ranking
        :param content: the rank_type of artwork to rank
        :param rank_type: the mode for ranking, daily, monthly etc ...
        :return: an object implement PikaxResult
        :rtype: PikaxResult
        """
        raise NotImplementedError

    def login(self, username: str = settings.username, password: str = settings.password) \
            -> (PikaxUserInterface, PikaxPagesInterface):
        raise NotImplementedError

    def download(self, pikax_result: PikaxResult, folder: str = None, illust_id: int = None) -> None:
        """
        Download all items given

        :param pikax_result: a PikaxResult to download, default None
        :param folder: the folder where artworks are download, default using folder in settings.py
        :param illust_id: the illust id to download, default None
        :rtype: None
        """
        raise NotImplementedError

    def visits(self, user_id: int) -> PikaxUserInterface:
        """
        Access a user in Pixiv given the user id with best available client

        :param user_id: the user id of the member in Pixiv
        :return: an object implement PikaxUserInterface
        :rtype: PikaxUserInterface
        """
        raise NotImplementedError


class BaseDownloader:

    @staticmethod
    def download_illust(artwork: Artwork, folder: str = None) -> Iterator[Tuple[Artwork.DownloadStatus, str]]:
        raise NotImplementedError

    @staticmethod
    def download_manga(artwork: Artwork, folder: str = None) -> Iterator[Tuple[Artwork.DownloadStatus, str]]:
        raise NotImplementedError

    def __init__(self):
        self.download_type_to_function = {
            params.DownloadType.ILLUST: self.download_illust,
            params.DownloadType.MANGA: self.download_manga,
        }

    # @staticmethod
    # def config_artworks(artworks: List[Artwork]):
    #     util.log('Configuring artworks', start=os.linesep, inform=True)
    #     total = len(artworks)
    #     config_artworks = []
    #     failed_config_artworks = dict()  # reason map to artwork
    #     pool = Pool()
    #
    #     def config_artwork(artwork_item):
    #         try:
    #             artwork_item.config()
    #             config_artworks.append(artwork_item)
    #         except ArtworkError as e:
    #             failed_config_artworks[str(e)] = artwork_item
    #
    #     for index, _ in enumerate(pool.imap_unordered(config_artwork, artworks)):
    #         util.print_progress(index + 1, total)
    #
    #     msg = f'expected: {total} | success: {len(config_artworks)} | failed: {len(failed_config_artworks)}'
    #     util.print_done(msg)
    #
    #     if failed_config_artworks:
    #         for index, item in enumerate(failed_config_artworks.items()):
    #             util.log(f'Artwork with id: {item[1].id} failed config for download: {item[0]}', error=True)
    #
    #     return config_artworks

    def download(self, pikax_result: PikaxResult, folder: str = ''):

        if not folder:
            folder = pikax_result.folder

        folder = util.clean_filename(folder)

        if folder and not os.path.isdir(folder):
            os.mkdir(folder)

        download_function = self.download_type_to_function[pikax_result.download_type]
        download_function = functools.partial(download_function, folder=folder)
        artworks = pikax_result.artworks
        successes = []
        fails = []
        skips = []
        total_pages = sum(len(artwork) for artwork in artworks)
        total_artworks = len(artworks)
        curr_page = 0
        curr_artwork = 0
        pool = Pool()
        util.log(f'Downloading Artworks | {total_pages} pages from {total_artworks} artworks', start=os.linesep,
                 inform=True)

        for download_details in pool.imap_unordered(download_function, artworks):
            curr_artwork += 1
            for download_detail in download_details:
                curr_page += 1
                if settings.MAX_PAGES_PER_ARTWORK and curr_page > settings.MAX_PAGES_PER_ARTWORK:
                    break
                status, msg = download_detail
                info = str(msg) + ' ' + str(status.value)
                if status is Artwork.DownloadStatus.OK:
                    successes.append(msg)
                elif status is Artwork.DownloadStatus.SKIPPED:
                    skips.append(msg)
                else:
                    fails.append(msg)
                info = f'{curr_artwork} / {total_artworks} ' \
                       f'=> {math.ceil((curr_artwork / total_artworks) * 100)}% | ' + info
                util.print_progress(curr_page, total_pages, msg=info)
        util.print_done()

        util.log(f'There are {len(successes)} downloaded pages', inform=True)

        util.log(f'There are {len(skips)} skipped pages', inform=True)
        for index, skip_info in enumerate(skips):
            util.log(skip_info, start=f' [{index + 1}] ', inform=True)

        util.log(f'There are {len(fails)} failed pages', inform=True)
        for index, skip_info in enumerate(fails):
            util.log(skip_info, start=f' [{index + 1}] ', inform=True)

        util.print_done(str(folder))
