import datetime

from .. import params, settings
from typing import Union
from ..api.models import Artwork


class PikaxResult:

    def __add__(self, other: 'PikaxResult') -> 'PikaxResult':
        raise NotImplementedError

    def __sub__(self, other: 'PikaxResult') -> 'PikaxResult':
        raise NotImplementedError

    def __getitem__(self, index: int) -> Artwork:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


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
             date: Union[str, datetime.datetime] = format(datetime.datetime.today(), '%Y%m%d'),
             type: params.Type = params.Type.ILLUST,
             rank_type: params.Rank = params.Rank.DAILY) \
            -> PikaxResult:
        raise NotImplementedError

    def search(self, keyword: str = '',
               type: params.Type = params.Type.ILLUST,
               match: params.Match = params.Match.EXACT,
               sort: params.Sort = params.Sort.DATE_DESC,
               range: datetime.timedelta = None,
               popularity: Union[int, str] = None,
               limit: int = None) \
            -> PikaxResult:
        raise NotImplementedError

    def access(self, user_id: int) -> PikaxUserInterface:
        raise NotImplementedError

    def login(self, username: str = settings.username, password: str = settings.password) \
            -> (PikaxUserInterface, PikaxPagesInterface):
        raise NotImplementedError
