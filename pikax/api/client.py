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
from ..exceptions import ReqException, ClientException, PikaxClientException
from .. import params


class BaseClient:
    # This class provide logged session and headers to use for making requests
    # Provide auto refreshing token functionalit
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

        self._login()

    def _update_access_token(self):
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self._refresh_token
        }
        try:
            self._auth_with_update(data)
        except ReqException as e:
            raise ClientException('Failed update access token') from e

    def _login(self):

        data = {
            'grant_type': 'password',
            'username': self._username,
            'password': self._password,
        }

        try:
            res_data = self._auth_with_update(data)
        except ReqException as e:
            raise ClientException('Failed login with username and password') from e

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

    def _is_access_token_outdated(self):
        time_ahead = 30  # return True if need refresh within 30s
        return (time.time() - self._access_token_start_time + time_ahead) > self._access_token_time_out

    def _update_token_if_outdated(self):
        if self._is_access_token_outdated():
            self._update_access_token()

    @property
    def session(self):
        self._update_token_if_outdated()
        return self._session

    @property
    def headers(self):
        self._update_token_if_outdated()
        return self._headers


class FunctionalBaseClient(BaseClient):
    # This class provide utilities for the real job, e.g. search/accessing user ...
    _host = 'https://app-api.pixiv.net'
    _search_url = _host + '/v1/search/{type}?'
    _following_url = _host + '/v1/user/following?'
    _collection_url = _host + '/v1/user/bookmarks/{collection_type}?'
    _tagged_collection_url = _host + '/v1/user/bookmark-tags/{collection_type}?'

    def __init__(self, username, password):
        super().__init__(username, password)

    @staticmethod
    def _get_search_start_url(keyword, type, match, sort, range):
        param = {
            'word': keyword
        }

        if type is not params.USER:
            param['search_target'] = match
            param['sort'] = sort

            if range:
                today = datetime.date.today()
                param['start_date'] = str(today)
                param['end_date'] = str(today - range)

        encoded_params = urllib.parse.urlencode(param)
        return FunctionalBaseClient._search_url.format(type=type.value) + encoded_params

    @staticmethod
    def _get_bookmarks_start_url(type, params, tagged):
        if tagged:
            collection_url = FunctionalBaseClient._tagged_collection_url.format(collection_type=type.value)
        else:
            collection_url = FunctionalBaseClient._collection_url.format(collection_type=type.value)

        encoded_params = urllib.parse.urlencode(params)
        return collection_url + encoded_params

    @staticmethod
    def _check_params(type=None, match=None, sort=None, range=None, limit=None, restrict=None):
        if (type is not None) and (not params.Search.Type.is_valid(type)):
            raise PikaxClientException(f'search type {type} must be an enum for {params.Search.Type}')
        if (match is not None) and (not params.Search.Match.is_valid(match)):
            raise PikaxClientException(f'search type {match} must be an enum for {params.Search.Match}')
        if (sort is not None) and (not params.Search.Sort.is_valid(sort)):
            raise PikaxClientException(f'search type {sort} must be an enum for {params.Search.Sort}')
        if (range is not None) and (not isinstance(range, datetime.timedelta)):
            raise PikaxClientException(f'search type {range} must be None or instance of datetime.timedelta')
        if (limit is not None) and (not isinstance(limit, int)):
            raise PikaxClientException(f'search type {limit} must be None or instance of int')
        if (restrict is not None) and (not params.Collections.Restrict.is_valid(restrict)):
            raise PikaxClientException(
                f'collections restrict {restrict} must be an enum for {params.Collections.Restrict}')

    @staticmethod
    def _check_bookmark_params(type):
        if type is not params.ILLUST and type is not params.NOVEL:
            raise PikaxClientException(f'invalid type {type} must be {params.ILLUST} or {params.NOVEL}')

    def _req(self, url, params=None):
        return util.req(url=url, session=self.session, headers=self.headers, params=params)

    def _get_ids(self, next_url, limit, type):
        data_container_name = params.Search.Type.get_response_container_name(type)
        ids_collected = []
        while next_url is not None and (not limit or len(ids_collected) < limit):
            res_data = self._req(next_url).json()
            if type is params.Search.Type.USER:
                ids_collected += [item['user']['id'] for item in res_data[data_container_name]]
            else:
                ids_collected += [item['id'] for item in res_data[data_container_name]]
            next_url = res_data['next_url']
            ids_collected = list(set(ids_collected))
        if limit:
            ids_collected = util.trim_to_limit(ids_collected, limit)
        return ids_collected

    def _get_bookmarks(self, type, limit, restrict, tagged, user_id):
        self._check_params(type=type, limit=limit, restrict=restrict)
        params = {
            'user_id': user_id,
            'restrict': restrict.value
        }
        start_url = self._get_bookmarks_start_url(type, params, tagged=tagged)
        return self._get_ids(start_url, limit=limit, type=type)


class Client(FunctionalBaseClient):
    # This class will be used by Pikax as api

    class User:
        def __init__(self, client, user_id):
            self._client = client
            self.user_id = user_id

        def bookmarks(self, type=params.ILLUST, limit=None, restrict=params.PUBLIC, tagged=False):
            ids = self._client._get_bookmarks(type=type, limit=limit, restrict=restrict, tagged=tagged,
                                              user_id=self.user_id)
            return ids

    def __init__(self, username, password):
        super().__init__(username, password)

    def search(self, keyword='', type=params.ILLUST, match=params.EXACT, sort=params.DATE_DESC, range=None, limit=None):
        # if user is passed in as type,
        # only keyword is considered

        self._check_params(type, match, sort, range, limit)

        start_url = self._get_search_start_url(keyword=keyword, type=type, match=match, sort=sort, range=range)
        ids = self._get_ids(start_url, limit=limit, type=type)

        # XXX attempt to fix user input keyword if no search result returned?
        # if not ids:
        #     auto_complete_keyword = self._get_keyword_match(word=keyword)
        #     if auto_complete_keyword:
        #         return self.search(keyword=auto_complete_keyword, type=type, match=match, sort=sort, range=range, limit=limit, r18=r18, r18g=r18g)

        return ids

    def bookmarks(self, type=params.ILLUST, limit=None, restrict=params.PUBLIC, tagged=False):
        self._check_bookmark_params(type)
        ids = self._get_bookmarks(type=type, limit=limit, restrict=restrict, tagged=tagged, user_id=self.user_id)
        return ids

    def visit(self, user_id):
        return Client.User(self, user_id)


# for testing
def main():
    from .. import settings
    client = Client(settings.username, settings.password)
    # time.sleep(10)
    # client._update_access_token()
    ids = client.bookmarks(restrict=params.PUBLIC)
    print(ids)
    print(len(ids))

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

    # url = 'https://accounts.pixiv.net/api/login?lang=en'
    # s = requests.Session()
    #
    # headers = {
    #     'Host': 'accounts.pixiv.net',
    #     'accept': 'application/json',
    #     'Origin': 'https://accounts.pixiv.net',
    #     'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-N950N Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36',
    #     'content-type': 'application/x-www-form-urlencoded',
    #     'Referer': 'https://accounts.pixiv.net/login?return_to=https%3A%2F%2Fwww.pixiv.net%2Fsetting_user.php%3Fref%3Dios-app&lang=en&source=touch&view_type=page',
    #     'Accept-Language': 'en-CN,en-US;q=0.9,en;q=0.8',
    # }


if __name__ == '__main__':
    main()
