import datetime
from typing import Union

from .. import params, settings
from pikax.v2.pikaxinterface import PikaxUserInterface, PikaxResult, PikaxPagesInterface
from .pikaxinterface import PikaxInterface
from .items import LoginHandler


class Pikax(PikaxInterface):

    def __init__(self, username=None, password=None):
        self.login_status = LoginHandler.LoginStatus.LOG_OUT
        if username and password:
            self.login(username, password)

    def access(self, user_id: int) -> PikaxUserInterface:
        pass

    def login(self, username: str = settings.username, password: str = settings.password) -> (
            PikaxUserInterface, PikaxPagesInterface):
        pass

    def search(self, keyword: str = '',
               type: params.Type = params.Type.ILLUST,
               match: params.Match = params.Match.EXACT,
               sort: params.Sort = params.Sort.DATE_DESC,
               range: datetime.timedelta = None,
               limit: int = None) \
            -> PikaxResult:
        pass

    def rank(self, limit: int = datetime.datetime,
             date: Union[str, datetime.datetime] = format(datetime.datetime.today(), '%Y%m%d'),
             type: params.Type = params.Type.ILLUST,
             rank_type: params.Rank = params.Rank.DAILY) \
            -> PikaxResult:
        pass

    def visits(self, user_id: int) -> PikaxUserInterface:
        pass
