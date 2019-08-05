
#
# This api is built smoothly thanks to @dazuling/@dazzler https://github.com/dazuling
#

#
# NOTE XXX This api is developing and not used by pikax yet
#


import datetime
import time
import urllib.parse

import requests
from .. import util
from ..exceptions import ReqException, ClientException
from .. import params

class Client:
    _auth_url = 'https://oauth.secure.pixiv.net/auth/token'
    _host = 'https://app-api.pixiv.net'
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
        self._headers = Client._headers.copy()

        # set after login
        self._access_token = None
        self._access_token_start_time = None
        self._refresh_token = None
        self._token_type = None
        # not used
        self._device_token = None

        self.user_id = None
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
            res = self._auth_with_update(data)
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
            url=Client._auth_url,
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


class _PikaxClient(Client):

    _search_url = Client._host + '/v1/search/illust?'

    def __init__(self, username, password):
        super().__init__(username, password)

    def _req(self, url):
        return util.req(url=url, session=self.session, headers=self.headers)

    def _get_search_start_url(self, keyword, match, sort, range):
        params = {
            'word': keyword,
            'search_target': match,
            'sort': sort
        }
        if range:
            today = datetime.date.today()
            params['start_date'] = str(today)
            params['end_date'] = str(today - range)

        encoded_params = urllib.parse.urlencode(params)
        return self._search_url + encoded_params


class PikaxClient(_PikaxClient):

    def __init__(self, username, password):
        super().__init__(username, password)

    def search(self, keyword=None, match=params.EXACT, sort=params.DATE_DESC, range=None, limit=None):
        next_url = self._get_search_start_url(keyword=keyword, match=match, sort=sort, range=range)
        ids_collected = []
        while next_url is not None and (not limit or len(ids_collected) < limit):
            res_data = self._req(next_url).json()
            ids_collected += [illust['id'] for illust in res_data['illusts']]
            next_url = res_data['next_url']
            time.sleep(1)
        if limit:
            ids_collected = util.trim_to_limit(ids_collected, limit)
        return ids_collected

# for testing
def main():
    username = 'restorecyclebin@gmail.com'
    password = '123456'
    client = PikaxClient(username, password)
    # time.sleep(10)
    # client._update_access_token()
    ids = client.search(keyword='arknights', limit=100)
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





if __name__ == '__main__':
    main()
