import datetime
import os
import pickle
import re
from typing import Union, List

from pikax import params
from ..exceptions import ReqException, LoginError

from .. import util, settings
from .models import APIUserInterface, APIPagesInterface


class BaseClient:
    _login_check_url = 'https://www.pixiv.net/touch/ajax/user/self/status'

    def __init__(self):
        self._session = util.new_session()
        self.cookies_file = settings.COOKIES_FILE

    def _check_is_logged(self):
        status_json = util.req(url=self._login_check_url, session=self._session).json()
        return status_json['body']['user_status']['is_logged_in']

    def _save_cookies(self):

        if os.path.isfile(self.cookies_file):
            util.log(f'Rewriting local cookie file: {self.cookies_file}')
        else:
            util.log(f'Saving cookies to local file: {self.cookies_file}')

        with open(self.cookies_file, 'wb') as file:
            pickle.dump(self._session.cookies, file)

    def _login(self, *args):
        raise NotImplementedError


class AccountClient(BaseClient):
    _login_url = 'https://accounts.pixiv.net/api/login?'
    _post_key_url = 'https://accounts.pixiv.net/login?'

    def __init__(self):
        super().__init__()

    def _login(self, username, password):
        postkey = self._get_postkey()

        data = {
            'password': password,
            'pixiv_id': username,
            'post_key': postkey,
        }
        params = {
            'lang': 'en'
        }

        util.log('Sending requests to attempt login ...')

        try:
            util.req(type='post', session=self._session, url=self._login_url, data=data, params=params)
        except ReqException as e:
            raise LoginError(f'Failed to send login request: {e}')

        util.log('Login request sent to Pixiv')
        if self._check_is_logged():
            self._save_cookies()
        else:
            raise LoginError('Login Request is not accepted')

    def _get_postkey(self):
        try:
            pixiv_login_page = util.req(session=self._session, url=self._post_key_url)
            post_key = re.search(r'post_key" value="(.*?)"', pixiv_login_page.text).group(1)
            util.log(f'Post key successfully retrieved: {post_key}')
            return post_key
        except (ReqException, AttributeError) as e:
            raise LoginError(f'Failed to find post key: {e}')


class CookiesClient(BaseClient):

    def __init__(self):
        super().__init__()

    def _login(self):
        try:
            self._local_cookies_login()
        except LoginError:
            try:
                self._user_cookies_login()
            except LoginError:
                raise LoginError('Cookies Login failed')

    def _local_cookies_login(self):

        if not os.path.exists(self.cookies_file):
            raise LoginError('Local Cookies file not found')

        # cookies exists
        util.log(f'Cookie file found: {self.cookies_file}, attempt to login with local cookie')
        try:
            with open(self.cookies_file, 'rb') as f:
                local_cookies = pickle.load(f)
                self._session.cookies = local_cookies
            if self._check_is_logged():
                util.log('Logged in successfully with local cookies', inform=True)
                return
            else:
                os.remove(self.cookies_file)
                util.log('Removed outdated cookies', inform=True)
        except pickle.UnpicklingError as e:
            os.remove(self.cookies_file)
            util.log('Removed corrupted cookies file, message: {}'.format(e))

        # local cookies failed
        raise LoginError('Login with cookies failed')

    def _user_cookies_login(self):
        msg = 'Login with local cookies failed, would you like to provide a new cookies?' + os.linesep \
              + ' [y] Yesss!' + os.linesep \
              + ' [n] Noooo! (Attempt alternate login with username and password)'
        util.log(msg, normal=True)

        while True:
            answer = input(' [=] Please select an option:').strip().lower()
            if answer in ['n', 'no']:
                break
            if answer not in ['y', 'yes']:
                print('Please enter your answer as case-insensitive \'y\', \'n\', \'yes\', \'no\'')
                continue

            cookies = input(' [=] Please enter your cookies here:')

            try:
                self._change_to_new_cookies(cookies)
                if self._check_is_logged():
                    self._save_cookies()
                    return
                else:
                    util.log('Failed login with cookies entered, would you like to try again? [y/n]', normal=True)
            except LoginError as e:
                util.log(f'cookies entered is invalid: {e}')
                util.log('would you like to try again? [y/n]')

        # user enter cookies failed
        raise LoginError('Failed login with user cookies')

    def _change_to_new_cookies(self, user_cookies):
        # remove old cookies
        for old_cookie in self._session.cookies.keys():
            self._session.cookies.__delitem__(old_cookie)

        # add new cookies
        try:
            for new_cookie in user_cookies.split(';'):
                name, value = new_cookie.split('=', 1)
                self._session.cookies[name] = value
        except ValueError as e:
            raise LoginError(f'Cookies given is invalid, please try again | {e}') from e


class WebClient(AccountClient, CookiesClient, APIUserInterface, APIPagesInterface):

    def __init__(self, username, password):
        super().__init__()
        try:
            AccountClient._login(self, username, password)
        except LoginError:
            try:
                CookiesClient._login(self)
            except LoginError:
                raise LoginError('Web client login failed')

    def bookmarks(self, limit: int = None) -> List[int]:
        pass

    def illusts(self, limit: int = None) -> List[int]:
        pass

    def novels(self, limit: int = None) -> List[int]:
        pass

    def mangas(self, limit: int = None) -> List[int]:
        pass

    def search(self, keyword: str = '', type: params.Type = params.Type.ILLUST,
               match: params.Match = params.Match.EXACT, sort: params.Sort = params.Sort.DATE_DESC,
               range: Union[datetime.timedelta, params.Range] = None, limit: int = None) -> List[int]:
        pass

    def rank(self, limit: int = None, date: Union[str, datetime.date] = format(datetime.date.today(), '%Y%m%d'),
             content: params.Content = params.Content.ILLUST, type: params.Rank = params.Rank.DAILY) -> List[int]:
        pass
