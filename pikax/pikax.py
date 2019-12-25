import datetime
from typing import Union

from . import params, settings, util
from .api.artwork import Illust
from .api.defaultclient import DefaultAPIClient
from .downloader import DefaultDownloader
from .items import LoginHandler
from .models import PikaxInterface, PikaxUserInterface, PikaxResult, PikaxPagesInterface
from .processor import DefaultIDProcessor
from .result import DefaultPikaxResult
from .user import DefaultPikaxUser


class Pikax(PikaxInterface):
    """
    The entry point of this api
    """

    def __init__(self, username=None, password=None):
        self._login_handler = LoginHandler()
        self.default_client = DefaultAPIClient()
        self.id_processor = DefaultIDProcessor()
        self.downloader = DefaultDownloader()
        self.username = password
        self.password = username
        self.web_client = None
        self.android_client = None

        if username and password:
            self.login()

    def login(self, username: str = settings.username, password: str = settings.password) -> (
            PikaxUserInterface, PikaxPagesInterface):
        """
        Attempt login using web and android method and returns the logged user
        if succeed, else returns None
        This method also saves logged client which used to perform other actions

        :param username: Username for login
        :param password: Password for login
        :return: a logged PikaxUser implemented PikaxUserInterface or None if failed
        :rtype: PikaxUserInterface or None
        """

        util.log('Attempting Login', inform=True)

        if username and password:
            self.username = username
            self.password = password

        status, client = self._login_handler.web_login(self.username, self.password)
        if status is LoginHandler.LoginStatus.PC:
            self.web_client = client
            util.log('successfully logged in as web user', inform=True)

        status, client = self._login_handler.android_login(self.username, self.password)
        if status is LoginHandler.LoginStatus.ANDROID:
            self.android_client = client
            util.log('successfully logged in as android user', inform=True)

        if not (self.android_client or self.web_client):
            util.log('failed login, using default client, some features will be unavailable', inform=True)
            return None

        logged_client = self._get_client()
        return DefaultPikaxUser(client=logged_client, user_id=logged_client.id)

    def search(self, keyword: str = '',
               search_type: params.SearchType = params.SearchType.ILLUST_OR_MANGA,
               match: params.Match = params.Match.PARTIAL,
               sort: params.Sort = params.Sort.DATE_DESC,
               search_range: datetime.timedelta = None,
               popularity: int = None,
               limit: int = None) \
            -> PikaxResult:
        """
        Search pixiv with best available client.
        Note that pixiv returns less result if not logged in

        :param keyword: the word to search
        :param search_type: rank_type of artwork to search
        :param match: define how strict the keywords are matched against artworks
        :param sort: order of the search result
        :param search_range: the date offset from today, can be a datetime.timedelta object
        :param popularity: if given, {popularity} users入り will be added after keywords
        :param limit: return number of artwork specified by limit, all by default
        :return: an object implement PikaxResult
        :rtype: PikaxResult
        """

        util.log(f'Searching {keyword} of rank_type {search_type} with limit {limit}', inform=True)

        client = self._get_client()
        if popularity:
            keyword = self._add_popularity_to_keyword(keyword, popularity)
        ids = client.search(keyword=keyword, search_type=search_type, match=match, sort=sort,
                            search_range=search_range, limit=limit)
        util.print_done(f'number of ids: {len(ids)}')
        process_type = self._get_process_from_search(search_type)
        download_type = self._get_download_from_process(process_type)
        success, fail = self._get_id_processor().process(ids, process_type=process_type)
        folder = settings.DEFAULT_SEARCH_FOLDER.format(keyword=keyword, search_type=search_type, match=match, sort=sort,
                                                       search_range=search_range, popularity=popularity, limit=limit)
        return DefaultPikaxResult(success, download_type=download_type, folder=folder)

    def rank(self, limit: int = None,
             date: Union[str, datetime.datetime] = format(datetime.datetime.today(), '%Y%m%d'),
             content: params.Content = params.Content.ILLUST,
             rank_type: params.RankType = params.RankType.DAILY) \
            -> PikaxResult:
        """
        Return the ranking artworks in pixiv according to parameters.
        This method returns complete artworks even if not logged in

        :param limit: the number of artworks to return
        :param date: the date of ranking
        :param content: the rank_type of artwork to rank
        :param rank_type: the mode for ranking, daily, monthly etc ...
        :return: an object implement PikaxResult
        :rtype: PikaxResult
        """

        util.log(f'Ranking date {date} of rank_type {rank_type} and content {content} with limit {limit}', inform=True)

        client = self._get_client()
        ids = client.rank(rank_type=rank_type, content=content, date=date, limit=limit)
        util.print_done(f'number of ids: {len(ids)}')
        process_type = self._get_process_from_content(content)
        download_type = self._get_download_from_process(process_type)
        success, fail = self._get_id_processor().process(ids, process_type=process_type)
        folder = settings.DEFAULT_RANK_FOLDER.format(limit=limit, date=date, content=content, rank_type=rank_type)
        return DefaultPikaxResult(success, download_type=download_type, folder=folder)

    def download(self, pikax_result=None, folder: str = '', illust_id: int = None) -> None:
        """
        Download all items given

        :param pikax_result: a PikaxResult to download, default None
        :param folder: the folder where artworks are download, default using folder in settings.py
        :param illust_id: the illust id to download, default None
        :rtype: None
        """
        if pikax_result:
            self.downloader.download(pikax_result=pikax_result, folder=folder)
        if illust_id:
            util.log(f'Initializing download with illust id: {illust_id}', inform=True)
            ill = Illust(illust_id=illust_id)
            self.downloader.download(pikax_result=DefaultPikaxResult([ill], download_type=params.DownloadType.ILLUST),
                                     folder=folder)

    def visits(self, user_id: int) -> PikaxUserInterface:
        """
        Access a user in Pixiv given the user id with best available client

        :param user_id: the user id of the member in Pixiv
        :return: an object implement PikaxUserInterface
        :rtype: PikaxUserInterface
        """
        client = self._get_client()
        return DefaultPikaxUser(client=client, user_id=user_id)

    def _get_client(self):
        if self.web_client:
            return self.web_client
        elif self.android_client:
            return self.android_client
        else:
            return self.default_client

    def _get_id_processor(self):
        return self.id_processor

    @staticmethod
    def _add_popularity_to_keyword(keyword, popularity):
        return str(keyword) + f' {popularity}users入り'

    @staticmethod
    def _get_process_from_search(search_type):
        return params.SearchType.map_search_to_process(
            search_type)

    @staticmethod
    def _get_download_from_process(process_type):
        return params.ProcessType.map_process_to_download(
            process_type)

    @staticmethod
    def _get_process_from_content(content):
        return params.Content.map_content_to_process(content)


def test():
    from . import settings
    import shutil
    pikax = Pikax(settings.username, settings.password)

    result = pikax.search(keyword='arknights', limit=15)
    test_folder = settings.TEST_FOLDER
    pikax.download(result, folder=test_folder)

    result = pikax.rank(limit=25)
    pikax.download(result, folder=test_folder)

    user = pikax.login(settings.username, settings.password)
    illusts = user.illusts()
    assert len(illusts) == 0, len(illusts)

    bookmarks = user.bookmarks(limit=30)
    assert len(bookmarks) == 30, len(bookmarks)

    mangas = user.mangas()
    assert len(mangas) == 0, len(mangas)

    user = pikax.visits(user_id=1113943)

    ill = user.illusts(limit=25)
    assert len(ill) == 25, len(ill)

    man = user.mangas(limit=10)
    assert len(man) == 10, len(man)

    col = user.bookmarks(limit=10)
    assert len(col) == 10, len(col)

    shutil.rmtree(test_folder)
    print(f'removed test folder: {test_folder}')

    print('successfully tested pikax')


def main():
    # test()
    from . import settings
    pixiv = Pikax()
    pixiv.login(settings.username, settings.password)
    res = pixiv.search(keyword='arknights', popularity=1000, limit=10)
    pixiv.download(res)


if __name__ == '__main__':
    main()
