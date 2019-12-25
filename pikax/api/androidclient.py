#
# special thanks @dazuling https://github.com/dazuling
# for explaining https://oauth.secure.pixiv.net/auth/token
#


import datetime
import hashlib
import time
import urllib.parse

import requests

from .defaultclient import DefaultAPIClient
from .models import APIUserInterface
from .. import params
from .. import util
from ..exceptions import ReqException, BaseClientException, ClientException, LoginError

__all__ = ['AndroidAPIClient']


class BaseClient:
    # This class provide auto-refreshing headers to use for making requests
    _auth_url = 'https://oauth.secure.pixiv.net/auth/token'
    __headers = {
        'User-Agent': 'PixivAndroidApp/5.0.151 (Android 5.1.1; SM-N950N)',
        'App-OS': 'android',
        'App-OS-Version': '5.1.1',
        'App-Version': '5.0.171',
    }
    _hash_secret = '28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c'

    def __init__(self, username, password):
        self._client_id = 'MOBrBDS8blbauoSck0ZfDbtuzpyT'
        self._client_secret = 'lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj'
        self._username = username
        self._password = password
        self._session = requests.Session()
        self._headers = BaseClient.__headers.copy()

        local_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')
        self._headers['X-Client-Time'] = local_time
        self._headers['X-Client-Hash'] = hashlib.md5((local_time + self._hash_secret).encode('utf-8')).hexdigest()

        # set after login
        self._access_token = None
        self._access_token_start_time = None
        self._refresh_token = None
        self._token_type = None

        self.user_id = None
        self._account = None
        self._name = None

        # not used
        self._device_token = None
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

        self._name = res_data['response']['user']['name']
        self._account = res_data['response']['user']['account']

        self.user_id = res_data['response']['user']['id']
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
            req_type='post',
            session=self._session,
            data=data,
            headers=self._headers
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
    _following_url = _host + '/v1/user/following?'
    _illust_creation_url = _host + '/v1/user/illusts?'
    _collection_url = _host + '/v1/user/bookmarks/{collection_type}?'
    _tagged_collection_url = _host + '/v1/user/bookmark-tags/{collection_type}?'

    def __init__(self, username, password):
        super().__init__(username, password)
        self._name = None
        self._account = None

    @classmethod
    def _get_search_start_url(cls, keyword, search_type, match, sort, search_range):
        cls._check_params(match=match, sort=sort, search_range=search_range)
        if search_type and not params.SearchType.is_valid(search_type):
            raise BaseClientException(f'search rank_type must be rank_type of {params.SearchType}')
        param = {'word': str(keyword), 'search_target': match.value, 'sort': sort.value}

        if search_range:
            if params.Range.is_valid(search_range):
                search_range = search_range.value
            today = datetime.date.today()
            param['start_date'] = str(today)
            param['end_date'] = str(today - search_range)

        encoded_params = urllib.parse.urlencode(param)
        return cls._search_url.format(type=search_type.value) + encoded_params

    @classmethod
    def _get_bookmarks_start_url(cls, bookmark_type, req_params, tagged):
        if bookmark_type and not params.BookmarkType.is_valid(bookmark_type):
            raise BaseClientException(f'bookmark rank_type: {bookmark_type} is not rank_type of {params.BookmarkType}')

        if tagged:
            collection_url = cls._tagged_collection_url.format(collection_type=bookmark_type.value)
        else:
            collection_url = cls._collection_url.format(collection_type=bookmark_type.value)

        encoded_params = urllib.parse.urlencode(req_params)
        return collection_url + encoded_params

    @classmethod
    def _get_creations_start_url(cls, req_params):
        encoded_params = urllib.parse.urlencode(req_params)
        return cls._illust_creation_url + encoded_params

    @staticmethod
    def _check_params(match=None, sort=None, search_range=None, restrict=None):
        if match and not params.Match.is_valid(match):
            raise BaseClientException(f'match: {match} is not rank_type of {params.Match}')
        if sort and not params.Sort.is_valid(sort):
            raise BaseClientException(f'sort: {sort} is not rank_type of {params.Sort}')
        if search_range and not params.Range.is_valid(search_range):
            raise BaseClientException(f'search_range: {search_range} is not rank_type of {params.Range}')
        if restrict and not params.Restrict.is_valid(restrict):
            raise BaseClientException(f'restrict: {restrict} is not rank_type of {params.Restrict}')

    def req(self, url, req_params=None):
        return util.req(url=url, headers=self.headers, params=req_params)

    def _get_ids(self, next_url, limit, id_type):
        if limit:
            limit = int(limit)
        data_container_name = params.Type.get_response_container_name(id_type.value)
        ids_collected = []
        while next_url is not None and (not limit or len(ids_collected) < limit):
            res_data = self.req(next_url).json()
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
        if bookmark_type is params.BookmarkType.ILLUST_OR_MANGA:
            bookmark_type = params.Type.ILLUST
        return self._get_ids(start_url, limit=limit, id_type=bookmark_type)

    def get_creations(self, creation_type, limit, user_id):
        if not params.CreationType.is_valid(creation_type):
            raise ClientException(
                f'creation rank_type must be rank_type of {params.CreationType}')

        req_params = {
            'user_id': int(user_id),
            'rank_type': creation_type.value
        }

        start_url = self._get_creations_start_url(req_params=req_params)
        return self._get_ids(start_url, limit=limit, id_type=creation_type)


class AndroidAPIClient(FunctionalBaseClient, DefaultAPIClient):
    # This class will be used by Pikax as api

    class User(APIUserInterface):
        _details_url = 'https://app-api.pixiv.net/v1/user/detail?'

        # This class represent other user
        def __init__(self, client, user_id):
            self.client = client
            self.user_id = user_id
            self._config()

        def _config(self):
            req_params = {
                'user_id': self.id
            }
            try:
                data = self.client.req(url=self._details_url + urllib.parse.urlencode(req_params)).json()
                self._account = data['user']['account']
                self._name = data['user']['name']
            except (ReqException, KeyError) as e:
                from ..exceptions import APIUserError
                raise APIUserError(f'Failed to config user details: {e}')

        def bookmarks(self, limit=None, bookmark_type=params.BookmarkType.ILLUST_OR_MANGA, tagged=None):
            return self.client.get_bookmarks(bookmark_type=bookmark_type, limit=limit, restrict=params.Restrict.PUBLIC,
                                             tagged=tagged, user_id=self.user_id)

        def illusts(self, limit=None):
            return self.client.get_creations(creation_type=params.CreationType.ILLUST, limit=limit,
                                             user_id=self.user_id)

        def mangas(self, limit=None):
            return self.client.get_creations(creation_type=params.CreationType.MANGA, limit=limit, user_id=self.user_id)

        @property
        def id(self):
            return self.user_id

        @property
        def account(self):
            return self._account

        @property
        def name(self):
            return self._name

    def __init__(self, username, password):
        FunctionalBaseClient.__init__(self, username, password)

    def search(self, keyword='', search_type=params.SearchType.ILLUST_OR_MANGA, match=params.Match.PARTIAL,
               sort=params.Sort.DATE_DESC,
               search_range=None, limit=None):
        # if params.user is passed in as rank_type,
        # only keyword is considered

        start_url = self._get_search_start_url(keyword=keyword, search_type=search_type, match=match, sort=sort,
                                               search_range=search_range)
        ids = self._get_ids(start_url, limit=limit, id_type=search_type)

        # XXX attempt to fix user input keyword if no search result returned?
        # if not ids:
        #     auto_complete_keyword = self._get_keyword_match(word=keyword)
        #     if auto_complete_keyword:
        #         return self.search(keyword=auto_complete_keyword, rank_type=rank_type, match=match, sort=sort,
        #                            range=range, limit=limit, r18=r18, r18g=r18g)

        return ids

    def rank(self, limit=None, date=format(datetime.date.today(), '%Y%m%d'), content=params.Content.ILLUST,
             rank_type=params.RankType.DAILY):
        return super().rank(limit=limit, date=date, content=content, rank_type=rank_type)

    def bookmarks(self, limit=None, bookmark_type: params.BookmarkType = params.BookmarkType.ILLUST_OR_MANGA,
                  restrict: params.Restrict = params.Restrict.PUBLIC):
        return self.get_bookmarks(bookmark_type=bookmark_type, limit=limit, restrict=restrict, tagged=False,  # XXX
                                  user_id=self.user_id)

    def illusts(self, limit=None):
        return self.get_creations(creation_type=params.CreationType.ILLUST, limit=limit, user_id=self.user_id)

    def mangas(self, limit=None):
        return self.get_creations(creation_type=params.CreationType.MANGA, limit=limit, user_id=self.user_id)

    def visits(self, user_id):
        return AndroidAPIClient.User(self, user_id)

    @property
    def account(self):
        return self._account

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self.user_id


def test():
    from .. import settings

    print('Testing AndroidClient')

    client = AndroidAPIClient(settings.username, settings.password)

    ids = client.search(keyword='arknights', limit=242, sort=params.Sort.DATE_DESC, match=params.Match.ANY,
                        search_range=params.Range.A_YEAR)
    assert len(ids) == 242, len(ids)

    ids = client.bookmarks(limit=30)
    assert len(ids) == 30, len(ids)

    ids = client.mangas(limit=0)
    assert len(ids) == 0, len(ids)

    ids = client.search(keyword='arknights', limit=234, sort=params.Sort.DATE_DESC,
                        search_type=params.SearchType.ILLUST_OR_MANGA,
                        match=params.Match.EXACT,
                        search_range=params.Range.A_YEAR)
    assert len(ids) == 234

    ids = client.rank(rank_type=params.RankType.ROOKIE, date=datetime.date.today(), content=params.Content.MANGA)
    assert len(ids) == 100, len(ids)

    user_id = 38088
    user = client.visits(user_id=user_id)
    user_illust_ids = user.illusts(limit=108)
    assert len(user_illust_ids) == 108, len(user_illust_ids)

    user_manga_ids = user.mangas(limit=2)
    assert len(user_manga_ids) == 2, len(user_manga_ids)

    print('Successfully tested Android Client')


def main():
    test()
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

