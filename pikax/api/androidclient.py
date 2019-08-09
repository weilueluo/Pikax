#
# special thanks @dazuling https://github.com/dazuling
# for explaining https://oauth.secure.pixiv.net/auth/token
#

#
# NOTE XXX This api is developing and not used by pikax yet
#


import datetime
import time
import urllib.parse

import requests
from .. import util
from ..exceptions import ReqException, BaseClientException, ClientException, LoginError
from .. import params

from .models import APIUserInterface
from .defaultclient import DefaultAPIClient

__all__ = ['AndroidClient']


class BaseClient:
    # This class provide auto-refreshing headers to use for making requests
    _auth_url = 'https://oauth.secure.pixiv.net/auth/token'
    _headers = {
        'User-Agent': 'PixivAndroidApp/5.0.151 (Android 5.1.1; SM-N950N)',
        'App-OS': 'android',
        'App-OS-Version': '5.1.1',
        'App-Version': '5.0.151',
        'Host': 'app-api.pixiv.net',
    }

    def __init__(self, username, password):
        self._client_id = 'MOBrBDS8blbauoSck0ZfDbtuzpyT'
        self._client_secret = 'lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj'
        self._username = username
        self._password = password
        self._session = requests.Session()
        self._headers = BaseClient._headers.copy()

        # set after login
        self._access_token = None
        self._access_token_start_time = None
        self._refresh_token = None
        self._token_type = None

        self.user_id = None

        # not used
        self._device_token = None
        self.name = None
        self.account = None
        self.mail = None
        self.is_auth_mail = None

        try:
            self._login()
        except ReqException as e:
            raise LoginError(str(e)) from e

    def _login(self):

        data = {
            'grant_type': 'password',
            'username': self._username,
            'password': self._password,
        }

        res_data = self._auth_with_update(data)

        self.user_id = res_data['response']['user']['id']
        self.name = res_data['response']['user']['name']
        self.account = res_data['response']['user']['account']
        self.mail = res_data['response']['user']['mail_address']
        self.is_auth_mail = res_data['response']['user']['is_mail_authorized']

    def _auth_with_update(self, extra_data):
        data = {
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'get_secure_url': 1,
            # https://github.com/dazuling/pixiv-api/blob/master/pixivapi/client.py#L154
            **extra_data
        }

        res = util.req(
            url=BaseClient._auth_url,
            type='post',
            session=self._session,
            data=data,
        ).json()

        self._access_token_start_time = time.time()
        self._access_token = res['response']['access_token']
        self._refresh_token = res['response']['refresh_token']
        self._token_type = res['response']['token_type']
        self._access_token_time_out = int(res['response']['expires_in'])  # time out for refresh token in seconds
        self._device_token = res['response']['device_token']
        self._headers.update({'Authorization': f'{self._token_type.title()} {self._access_token}'})

        return res

    def _update_token_if_outdated(self):
        if self._is_access_token_outdated():
            self._update_access_token()

    def _is_access_token_outdated(self):
        time_ahead = 30  # return True if need refresh within 30s
        return (time.time() - self._access_token_start_time + time_ahead) > self._access_token_time_out

    def _update_access_token(self):
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self._refresh_token
        }
        try:
            self._auth_with_update(data)
        except ReqException as e:
            raise BaseClientException('Failed update access token') from e

    @property
    def headers(self):
        self._update_token_if_outdated()
        return self._headers


class FunctionalBaseClient(BaseClient):
    # This class provide utilities for the real job, e.g. search/accessing user ...
    _host = 'https://app-api.pixiv.net'
    _search_url = _host + '/v1/search/{type}?'
    _illust_creation_url = _host + '/v1/user/illusts?'
    _novel_creation_url = _host + '/v1/user/novels?'
    _following_url = _host + '/v1/user/following?'
    _collection_url = _host + '/v1/user/bookmarks/{collection_type}?'
    _tagged_collection_url = _host + '/v1/user/bookmark-tags/{collection_type}?'

    def __init__(self, username, password):
        super().__init__(username, password)

    @classmethod
    def _get_search_start_url(cls, keyword, search_type, match, sort, search_range):
        cls._check_params(match=match, sort=sort, search_range=search_range)
        if search_type not in [params.ILLUST, params.NOVEL, params.USER]:
            raise ClientException(f'search type must be either {params.ILLUST}, {params.NOVEL} or {params.USER}')
        param = {
            'word': str(keyword)
        }

        if search_type is not params.USER:
            param['search_target'] = match.value
            param['sort'] = sort.value

            if search_range:
                today = datetime.date.today()
                param['start_date'] = str(today)
                param['end_date'] = str(today - search_range)

        encoded_params = urllib.parse.urlencode(param)
        return cls._search_url.format(type=search_type.value) + encoded_params

    @classmethod
    def _get_bookmarks_start_url(cls, bookmark_type, req_params, tagged):
        if bookmark_type not in [params.ILLUST, params.NOVEL]:
            raise ClientException(f'Invalid type: {bookmark_type}, accepts {params.ILLUST} and {params.NOVEL} only')

        if tagged:
            collection_url = cls._tagged_collection_url.format(collection_type=bookmark_type.value)
        else:
            collection_url = cls._collection_url.format(collection_type=bookmark_type.value)

        encoded_params = urllib.parse.urlencode(req_params)
        return collection_url + encoded_params

    @classmethod
    def _get_creations_start_url(cls, req_params, creation_type):
        encoded_params = urllib.parse.urlencode(req_params)
        if creation_type is params.Type.NOVELS:
            return cls._novel_creation_url + encoded_params
        else:
            return cls._illust_creation_url + encoded_params

    @staticmethod
    def _check_params(match=None, sort=None, search_range=None, restrict=None):
        if (match is not None) and (not params.Match.is_valid(match)):
            raise ClientException(f'search type: {match} is not in {params.Match}')
        if (sort is not None) and (not params.Sort.is_valid(sort)):
            raise ClientException(f'search type: {sort} is not in {params.Sort}')
        if (search_range is not None) and (not isinstance(search_range, datetime.timedelta)):
            raise ClientException(f'search type: {search_range} is not None or instance of datetime.timedelta')
        if (restrict is not None) and (not params.Collections.Restrict.is_valid(restrict)):
            raise ClientException(
                f'collections restrict {restrict} is not in {params.Collections.Restrict}')

    def _req(self, url, req_params=None):
        return util.req(url=url, headers=self.headers, params=req_params)

    def _get_ids(self, next_url, limit, id_type):
        if limit:
            limit = int(limit)
        data_container_name = params.Type.get_response_container_name(id_type)
        ids_collected = []
        while next_url is not None and (not limit or len(ids_collected) < limit):
            res_data = self._req(next_url).json()
            if id_type is params.Type.USER:
                ids_collected += [item['user']['id'] for item in res_data[data_container_name]]
            else:
                ids_collected += [item['id'] for item in res_data[data_container_name]]
            next_url = res_data['next_url']
            ids_collected = list(set(ids_collected))
        if limit:
            ids_collected = util.trim_to_limit(ids_collected, limit)
        return ids_collected

    def get_bookmarks(self, bookmark_type, limit, restrict, tagged, user_id):
        self._check_params(restrict=restrict)

        req_params = {
            'user_id': int(user_id),
            'restrict': restrict.value
        }
        start_url = self._get_bookmarks_start_url(bookmark_type, req_params, tagged=tagged)
        return self._get_ids(start_url, limit=limit, id_type=bookmark_type)

    def get_creations(self, creation_type, limit, user_id):
        if creation_type not in [params.ILLUST, params.MANGA, params.NOVEL]:
            raise ClientException(f'creation type must be either {params.ILLUST} or {params.MANGA}')

        req_params = {
            'user_id': int(user_id),
        }

        if creation_type is params.NOVEL:
            creation_type = params.Type.NOVELS  # novel is novels in the android endpoint requests respond
        else:
            req_params['type'] = creation_type.value

        start_url = self._get_creations_start_url(req_params=req_params, creation_type=creation_type)
        return self._get_ids(start_url, limit=limit, id_type=creation_type)


class AndroidClient(FunctionalBaseClient, DefaultAPIClient):
    # This class will be used by Pikax as api

    class User(APIUserInterface):
        # This class represent other user
        def __init__(self, client, user_id):
            self.client = client
            self.user_id = user_id

        def bookmarks(self, type=params.ILLUST, limit=None, tagged=False):
            return self.client.get_bookmarks(bookmark_type=type, limit=limit, restrict=params.PUBLIC, tagged=tagged,
                                             user_id=self.user_id)

        def illusts(self, limit=None):
            return self.client.get_creations(creation_type=params.ILLUST, limit=limit, user_id=self.user_id)

        def novels(self, limit=None):
            return self.client.get_creations(creation_type=params.NOVEL, limit=limit, user_id=self.user_id)

        def mangas(self, limit=None):
            return self.client.get_creations(creation_type=params.MANGA, limit=limit, user_id=self.user_id)

    def __init__(self, username, password):
        FunctionalBaseClient.__init__(self, username, password)

    def search(self, keyword='', type=params.ILLUST, match=params.EXACT, sort=params.DATE_DESC, range=None, limit=None):
        # if params.user is passed in as type,
        # only keyword is considered

        start_url = self._get_search_start_url(keyword=keyword, search_type=type, match=match, sort=sort,
                                               search_range=range)
        ids = self._get_ids(start_url, limit=limit, id_type=type)

        # XXX attempt to fix user input keyword if no search result returned?
        # if not ids:
        #     auto_complete_keyword = self._get_keyword_match(word=keyword)
        #     if auto_complete_keyword:
        #         return self.search(keyword=auto_complete_keyword, type=type, match=match, sort=sort, range=range, limit=limit, r18=r18, r18g=r18g)

        return ids

    def rank(self, limit=None, date=str(datetime.date.today()), content=params.Content.ILLUST,
             type=params.Rank.DAILY):
        return super().rank(limit=limit, date=date, content=content, type=type)

    def bookmarks(self, type=params.ILLUST, limit=None, restrict=params.PUBLIC, tagged=False):
        return self.get_bookmarks(bookmark_type=type, limit=limit, restrict=restrict, tagged=tagged,
                                  user_id=self.user_id)

    def novels(self, limit=None):
        return self.get_creations(creation_type=params.NOVEL, limit=limit, user_id=self.user_id)

    def illusts(self, limit=None):
        return self.get_creations(creation_type=params.ILLUST, limit=limit, user_id=self.user_id)

    def mangas(self, limit=None):
        return self.get_creations(creation_type=params.MANGA, limit=limit, user_id=self.user_id)

    def visits(self, user_id):
        return AndroidClient.User(self, user_id)


#
# for testing
#
def test():
    from .. import settings

    print('Testing AndroidClient')

    client = AndroidClient(settings.username, settings.password)

    ids = client.search(keyword='arknights', limit=242, sort=params.DATE_DESC, match=params.ANY, range=params.A_YEAR)
    assert len(ids) == 242, len(ids)

    ids = client.bookmarks(limit=30)
    assert len(ids) == 30, len(ids)

    ids = client.mangas(limit=0)
    assert len(ids) == 0, len(ids)

    ids = client.novels(limit=0)
    assert len(ids) == 0, len(ids)

    novel_writer = client.visits(user_id=24118759)

    ids = novel_writer.bookmarks(limit=100)
    assert len(ids) == 100, len(ids)

    ids = novel_writer.bookmarks(type=params.NOVEL, limit=17)
    assert len(ids) == 17, len(ids)

    ids = novel_writer.novels(limit=3)
    assert len(ids) == 3, len(ids)

    ids = novel_writer.illusts(limit=0)
    assert len(ids) == 0, len(ids)


def main():
    test()
    # from .. import settings
    # client = AndroidClient(settings.username, settings.password)
    # user = client.visits(user_id=24118759)
    #
    # print(type(user.novels()[0]))

    # while True:
    #     try:
    #         res = util.req(url=url, session=client._session, headers=client._headers, params=params)
    #     except ReqException as e:
    #         print(e)
    #         print('Failed request, trying to refresh token ...')
    #         client._update_access_token()
    #         print('+' * 50)
    #         continue
    #     print(res)
    #     print(time.time() - client._access_token_start_time)
    #     print('=' * 10)
    #     time.sleep(10)


if __name__ == '__main__':
    main()
