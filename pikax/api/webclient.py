import datetime
import os
import pickle
import re
from typing import Union, List

from .. import params
from .. import settings
from .. import util
from ..api.defaultclient import DefaultAPIClient, DefaultAPIUser
from ..exceptions import ReqException, LoginError, APIUserError
from ..texts import texts

__all__ = ['WebAPIClient']


class BaseClient:
    _login_check_url = 'https://www.pixiv.net/touch/ajax/user/self/status'

    def __init__(self):
        self._session = util.new_session()
        self.cookies_file = settings.COOKIES_FILE

    def _check_is_logged(self):
        try:
            status_json = util.req(url=self._login_check_url, session=self._session).json()
            return status_json['body']['user_status']['is_logged_in']
        except ReqException:
            util.log(texts.CHECK_LOGIN_FAILED)
            return False

    def _save_cookies(self):

        if os.path.isfile(self.cookies_file):
            util.log(texts.OVERWRITE_LOCAL_COOKIES.format(file=self.cookies_file))
        else:
            util.log(texts.SAVE_LOCAL_COOKIES.format(file=self.cookies_file))

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
        login_params = {
            'lang': 'en'
        }

        util.log(texts.ATTEMPT_WEB_CLIENT_LOGIN)

        try:
            util.req(req_type='post', session=self._session, url=self._login_url, data=data, params=login_params)
        except ReqException as e:
            raise LoginError(texts.WEB_LOGIN_REQUEST_FAILED.format(e=e))

        util.log('Login request sent to Pixiv')
        if self._check_is_logged():
            self._save_cookies()
        else:
            raise LoginError(texts.WEB_LOGIN_REQUEST_NOT_ACCEPTED)

    def _get_postkey(self):
        try:
            pixiv_login_page = util.req(session=self._session, url=self._post_key_url)
            post_key = re.search(r'post_key" value="(.*?)"', pixiv_login_page.text).group(1)
            util.log(texts.WEB_LOGIN_POST_KEY_RETRIEVE_SUCCESS.format(post_key=post_key))
            return post_key
        except (ReqException, AttributeError) as e:
            raise LoginError(texts.WEB_LOGIN_POST_KEY_RETRIEVE_Failed.format(e=e))


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
                raise LoginError(texts.COOKIE_LOGIN_FAILED)

    def _local_cookies_login(self):

        if not os.path.exists(self.cookies_file):
            raise LoginError(texts.COOKIE_FILE_NOT_FOUND.format(file=self.cookies_file))

        # cookies exists
        util.log(texts.COOKIE_FILE_FOUND.format(file=self.cookies_file))
        try:
            with open(self.cookies_file, 'rb') as f:
                local_cookies = pickle.load(f)
                self._session.cookies = local_cookies
            if self._check_is_logged():
                util.log(texts.COOKIE_LOGIN_SUCCESS, inform=True)
                return
            else:
                os.remove(self.cookies_file)
                util.log(texts.REMOVED_OUTDATED_COOKIE, inform=True)
        except pickle.UnpicklingError as e:
            os.remove(self.cookies_file)
            util.log(texts.REMOVED_CORRUPTED_COOKIE.format(e))

        # local cookies failed
        raise LoginError(texts.COOKIE_LOGIN_FAILED)

    def _user_cookies_login(self):
        util.log(texts.PROVIDE_NEW_COOKIE_PROMPT, normal=True)

        while True:
            answer = input(texts.PROVIDE_NEW_COOKIE_PROMPT_ASK).strip().lower()
            if answer in ['n', 'no']:
                break
            if answer not in ['y', 'yes']:
                print(texts.INVALID_RESPOND_PROMPT)
                continue

            cookies = input(texts.ENTER_NEW_COOKIE_PROMPT)

            try:
                self._change_to_new_cookies(cookies)
                if self._check_is_logged():
                    self._save_cookies()
                    return
                else:
                    util.log(texts.NEW_COOKIE_LOGIN_FAILD, normal=True)
            except LoginError as e:
                util.log(texts.COOKIE_ENTERED_INVALID.format(e=e))
                util.log(texts.TRY_AGAIN_PROMPT)

        # user enter cookies failed
        raise LoginError(texts.COOKIE_LOGIN_FAILED)

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
            raise LoginError(texts.COOKIE_ENTERED_INVALID.format(e=e)) from e


class BookmarkHandler:
    _bookmark_url = 'https://www.pixiv.net/ajax/user/{user_id}/illusts/bookmarks?'

    @classmethod
    def _check_params(cls, limit, bookmark_type, restrict):
        if limit and not isinstance(limit, int):
            raise APIUserError(texts.BOOKMARK_INVALID_LIMIT)
        if bookmark_type and not params.BookmarkType.is_valid(bookmark_type):
            raise APIUserError(texts.INVALID_BOOKMARK_TYPE_ERROR.format(bookmark_type=bookmark_type,
                                                                        bookmark_types=params.BookmarkType))
        if restrict and not params.Restrict.is_valid(restrict):
            raise APIUserError(texts.INVALID_RESTRICT_TYPE_ERROR.format(restrict_type=restrict,
                                                                        restrict_types=params.Restrict))

    @classmethod
    def _set_params(cls, bookmark_type, restrict, user_id):
        req_params = dict()
        req_params['limit'] = 1
        req_params['offset'] = 0
        req_params['tag'] = ''
        req_params['user_id'] = int(user_id)
        if bookmark_type:
            if bookmark_type is params.BookmarkType.ILLUST_OR_MANGA:
                pass  # this is the default

        if restrict:
            if restrict is params.Restrict.PUBLIC:
                req_params['rest'] = 'show'
            elif restrict is params.Restrict.PRIVATE:
                req_params['rest'] = 'hide'

        return req_params

    @classmethod
    def bookmarks(cls, limit, bookmark_type, restrict, user_id, session):
        cls._check_params(limit, bookmark_type, restrict)

        req_params = cls._set_params(bookmark_type, restrict, user_id)

        try:
            url = cls._bookmark_url.format(user_id=user_id)
            data = util.req(url=url, params=req_params, session=session).json()
            req_params['limit'] = data['body']['total']
            data = util.req(url=url, params=req_params, session=session).json()
            ids = [item['id'] for item in data['body']['works']]
            return util.trim_to_limit(ids, limit=limit)
        except (ReqException, KeyError) as e:
            raise APIUserError(texts.USER_BOOKMARKS_RETRIEVE_FAILED.format(id=user_id)) from e


class CreationHandler:
    _illusts_url = 'https://www.pixiv.net/touch/ajax/illust/user_illusts?user_id={user_id}'
    _content_url = 'https://www.pixiv.net/touch/ajax/user/illusts?'

    @classmethod
    def illusts(cls, user_id, session, limit):
        try:
            res = util.req(session=session, url=cls._illusts_url.format(user_id=user_id))
            illust_ids = eval(res.text)  # string to list
            return util.trim_to_limit(illust_ids, limit)
        except ReqException as e:
            raise APIUserError(texts.USER_ILLUST_RETRIEVE_FAILED.format(id=user_id)) from e

    @classmethod
    def mangas(cls, user_id, session, limit):
        req_params = dict()
        req_params['id'] = user_id
        req_params['type'] = 'manga'
        curr_page = 0
        last_page = 1  # a number more than curr_page
        manga_ids = []

        try:
            while curr_page < last_page:
                curr_page += 1

                req_params['p'] = curr_page
                data = util.req(session=session, url=cls._content_url, params=req_params).json()
                manga_ids += [illust['id'] for illust in data['illusts']]
                if limit:
                    if len(manga_ids) > limit:
                        manga_ids = util.trim_to_limit(items=manga_ids, limit=limit)
                        break
                last_page = data['lastPage']
        except (ReqException, KeyError) as e:
            raise APIUserError(texts.USER_MANGA_RETRIEVE_FAILED.format(id=user_id)) from e

        return manga_ids


class WebAPIUser(DefaultAPIUser):

    def bookmarks(self, limit: int = None, bookmark_type: params.Type = params.Type.ILLUST,
                  restrict: params.Restrict = params.Restrict.PUBLIC) -> List[int]:
        return BookmarkHandler.bookmarks(bookmark_type=bookmark_type, restrict=restrict, limit=limit,
                                         session=self._session, user_id=self.id)


@DeprecationWarning
class WebAPIClient(AccountClient, CookiesClient, DefaultAPIClient):
    _self_details_url = 'https://www.pixiv.net/touch/ajax/user/self/status'

    def __init__(self, username, password):
        super().__init__()
        try:
            AccountClient._login(self, username, password)
        except LoginError:
            try:
                CookiesClient._login(self)
            except LoginError as e:
                raise LoginError(texts.WEB_LOGIN_FAILED.format(e=e))

        DefaultAPIClient.__init__(self._session)
        self._config()

    def _config(self):
        try:
            data = util.req(url=self._self_details_url, session=self._session).json()
            self._name = data['body']['user_status']['user_name']
            self._id = data['body']['user_status']['user_id']
            self._account = data['body']['user_status']['user_account']
            self.user = self.visits(self.id)
        except (ReqException, KeyError) as e:
            raise APIUserError(texts.WEB_CLIENT_CONFIGURE_FAILED.format(e=e)) from e

    def bookmarks(self, limit: int = None, bookmark_type: params.BookmarkType = params.BookmarkType.ILLUST_OR_MANGA,
                  restrict: params.Restrict = params.Restrict.PUBLIC) -> List[int]:
        return BookmarkHandler.bookmarks(limit=limit, bookmark_type=bookmark_type, restrict=restrict, user_id=self.id,
                                         session=self._session)

    def illusts(self, limit: int = None) -> List[int]:
        return CreationHandler.illusts(user_id=self.id, limit=limit, session=self._session)

    def mangas(self, limit: int = None) -> List[int]:
        return CreationHandler.mangas(user_id=self.id, session=self._session, limit=limit)

    def search(self, keyword: str = '', search_type: params.SearchType = params.SearchType.ILLUST_OR_MANGA,
               match: params.Match = params.Match.PARTIAL, sort: params.Sort = params.Sort.DATE_DESC,
               search_range: Union[datetime.timedelta, params.Range] = None, limit: int = None) -> List[int]:
        return super().search(keyword=keyword, search_type=search_type, match=match, sort=sort,
                              search_range=search_range, limit=limit)

    def rank(self, limit: int = None, date: Union[str, datetime.date] = format(datetime.date.today(), '%Y%m%d'),
             content: params.Content = params.Content.ILLUST, rank_type: params.RankType = params.RankType.DAILY) -> \
            List[int]:
        return super().rank(rank_type=rank_type, date=date, content=content, limit=limit)

    def visits(self, user_id: int):
        return WebAPIUser(user_id=user_id, session=self._session)

    @property
    def account(self):
        return self._account

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id
