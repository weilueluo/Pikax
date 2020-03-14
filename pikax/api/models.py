import datetime
import enum
import os
from multiprocessing.dummy import Pool
from typing import List, Tuple, Union, Type, Any

from .. import params, util
from ..exceptions import ArtworkError
from ..texts import texts

__all__ = ['APIAccessInterface', 'APIPagesInterface', 'APIUserInterface', 'Artwork', 'BaseIDProcessor']


class APIUserInterface:

    def bookmarks(self, limit: int = None, bookmark_type: params.BookmarkType = params.BookmarkType.ILLUST_OR_MANGA,
                  restrict: params.Restrict = params.Restrict.PUBLIC) -> List[int]:
        raise NotImplementedError

    def illusts(self, limit: int = None) -> List[int]: raise NotImplementedError

    def mangas(self, limit: int = None) -> List[int]: raise NotImplementedError

    @property
    def id(self): raise NotImplementedError

    @property
    def name(self): raise NotImplementedError

    @property
    def account(self): raise NotImplementedError


class APIAccessInterface:
    def visits(self, user_id: int) -> APIUserInterface:
        raise NotImplementedError


class APIPagesInterface:

    def search(self, keyword: str = '',
               search_type: params.Type = params.Type.ILLUST,
               match: params.Match = params.Match.PARTIAL,
               sort: params.Sort = params.Sort.DATE_DESC,
               search_range: Union[datetime.timedelta, params.Range] = None,
               limit: int = None) -> List[int]: raise NotImplementedError

    def rank(self,
             rank_type: params.RankType = params.RankType.DAILY,
             content: params.Content = params.Content.ILLUST,
             date: Union[str, datetime.date] = format(datetime.date.today(), '%Y%m%d'),
             limit: int = None) -> List[int]: raise NotImplementedError


class Artwork:

    def __init__(self, artwork_id):
        self._id = artwork_id
        self.config()

    def __hash__(self):
        return self.id

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

    @property
    def id(self):
        return self._id

    @property
    def width(self): raise NotImplementedError

    @property
    def height(self): raise NotImplementedError

    class DownloadStatus(enum.Enum):
        OK = texts.DOWNLOAD_STATUS_OK
        SKIPPED = texts.DOWNLOAD_STATUS_SKIP
        FAILED = texts.DOWNLOAD_STATUS_FAIL

    # return download status, content, filename
    def __getitem__(self, index) -> Tuple[DownloadStatus, Any, str]: raise NotImplementedError

    # return num of pages
    def __len__(self): raise NotImplementedError

    # test if two artwork has the same id
    def __eq__(self, other): raise NotImplementedError

    # test if two artwork has different id
    def __ne__(self, other): raise NotImplementedError

    # set variables, raises ReqException if fails,
    # it is called in the __init__ method
    # you should not need to call this unless
    # artwork configure failed and you want to try again,
    def config(self): raise NotImplementedError


class BaseIDProcessor:

    def __init__(self):
        self.type_to_function = {
            params.ProcessType.MANGA: self.process_mangas,
            params.ProcessType.ILLUST: self.process_illusts,
        }

    def process_illusts(self, ids: List[int]) -> Tuple[List[Artwork], List[int]]:
        raise NotImplementedError

    def process_mangas(self, ids: List[int]) -> Tuple[List[Artwork], List[int]]:
        raise NotImplementedError

    def process(self, ids: List[int], process_type: params.ProcessType) -> Tuple[List[Artwork], List[int]]:
        if not params.ProcessType.is_valid(process_type):
            from ..exceptions import ProcessError
            raise ProcessError(texts.INVALID_PROCESS_TYPE_ERROR.format(process_type=process_type,
                                                                       process_types=params.ProcessType))

        return self.type_to_function[process_type](ids)

    @staticmethod  # param cls is pass in as argument
    def _general_processor(cls: Type[Artwork], item_ids: List[int]) -> Tuple[List[Artwork], List[int]]:
        util.log(texts.ARTWORK_ID_PROCESSING, start=os.linesep, inform=True)
        total = len(item_ids)
        successes = []
        fails = []
        pool = Pool()

        def process_item(item_id_):
            try:
                successes.append(cls(item_id_))
            except ArtworkError:
                fails.append(item_id_)

        for index, item_id in enumerate(pool.imap_unordered(process_item, item_ids), 1):
            util.print_progress(index, total, msg=texts.GUI_ID_PROCESSING_HEADING)
        msg = texts.ARTWORK_ID_PROCESS_RESULT.format(total=total, successes=len(successes), fails=len(fails))
        util.print_done(msg)
        return successes, fails
