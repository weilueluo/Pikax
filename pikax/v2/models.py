import datetime
import operator
import os

from .. import params, settings, util
from typing import Union, List, Type
from ..api.models import Artwork


class PikaxResult:

    def __init__(self, artworks: List[Type[Artwork]], folder: str = ''):
        if any(not issubclass(artwork, Artwork) for artwork in artworks):
            from ..exceptions import PikaxResultError
            raise PikaxResultError(f'artworks must all be subclass of {Artwork}')

        self._artworks = artworks
        self._folder = str(folder)
        self._likes = self.ComparableItem(self, PikaxResult, 'likes')
        self._bookmarks = self.ComparableItem(self, PikaxResult, 'bookmarks')
        self._views = self.ComparableItem(self, PikaxResult, 'views')

    def __add__(self, other: 'PikaxResult') -> 'PikaxResult':
        raise NotImplementedError

    def __sub__(self, other: 'PikaxResult') -> 'PikaxResult':
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

        def __init__(self, outer_self, outer_class, name):
            self.name = name
            self.outer_self = outer_self
            self.outer_class = outer_class

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
            result = self.outer_class(new_artworks, folder)

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


class PikaxUserInterface:

    def illusts(self, limit: int = None) -> PikaxResult:
        raise NotImplementedError

    def novels(self, limit: int = None) -> PikaxResult:
        raise NotImplementedError

    def mangas(self, limit: int = None) -> PikaxResult:
        raise NotImplementedError

    def bookmarks(self, limit: int = None, type: params.Type = params.Type.ILLUST) -> PikaxResult:
        raise NotImplementedError


class PikaxPagesInterface:

    def search(self, keyword: str = '',
               type: params.Type = params.Type.ILLUST,
               match: params.Match = params.Match.EXACT,
               sort: params.Sort = params.Sort.DATE_DESC,
               range: datetime.timedelta = None,
               limit: int = None) \
            -> PikaxResult:
        raise NotImplementedError

    def rank(self,
             limit: int = None,
             date: Union[str, datetime.datetime] = format(datetime.datetime.today(), '%Y%m%d'),
             type: params.Type = params.Type.ILLUST,
             rank_type: params.Rank = params.Rank.DAILY) \
            -> PikaxResult:
        raise NotImplementedError


class PikaxInterface(PikaxPagesInterface):

    def rank(self,
             limit: int = None,
             date: Union[str, datetime.datetime] = format(datetime.date.today(), '%Y%m%d'),
             content: params.Type = params.Type.ILLUST,
             rank_type: params.Rank = params.Rank.DAILY) \
            -> PikaxResult:
        raise NotImplementedError

    def search(self, keyword: str = '',
               search_type: params.Type = params.Type.ILLUST,
               match: params.Match = params.Match.EXACT,
               sort: params.Sort = params.Sort.DATE_DESC,
               search_range: datetime.timedelta = None,
               popularity: Union[int, str] = None,
               limit: int = None) \
            -> PikaxResult:
        raise NotImplementedError

    def access(self, user_id: int) -> PikaxUserInterface:
        raise NotImplementedError

    def login(self, username: str = settings.username, password: str = settings.password) \
            -> (PikaxUserInterface, PikaxPagesInterface):
        raise NotImplementedError
