import datetime
import enum
from typing import List, Tuple, Union, Type
from .. import params
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
               match: params.Match = params.Match.EXACT,
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
        OK = 'OK'
        SKIPPED = 'skipped'
        FAILED = 'failed'

    # return download status, content, filename
    def __getitem__(self, index): raise NotImplementedError

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
        if process_type not in [params.ProcessType.ILLUST, params.ProcessType.NOVEL, params.ProcessType.MANGA, params.ProcessType.GIF]:
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
