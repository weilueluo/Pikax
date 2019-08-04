# -*- coding: utf-8 -*-

"""
This module contains classes representing different pages in Pixiv.net
Each page encapsulate their capabilities

**Classes**
:class: LoginPage
:class: SearchPage
:class: RankingPage
"""

import json
import re
import requests
import time

from . import settings, util
from .exceptions import LoginError, ReqException, PostKeyError, SearchError, RankError

__all__ = ['LoginPage', 'SearchPage', 'RankingPage']


# raise LoginError if failed to login
class LoginPage:
    """Representing login page in pixiv.net

    :func login: used to attempt login
    """
    _post_key_url = 'https://accounts.pixiv.net/login?'
    _post_key_req_type = 'get'
    _login_url = 'https://accounts.pixiv.net/api/login?lang=en'

    def __init__(self):
        self.password = None
        self.username = None
        self.post_key = None
        self._session = requests.Session()

    def relogin_with_cookies(self):
        cookies = input('Paste your cookies:')
        for old_cookie in self._session.cookies.keys():
            self._session.cookies.__delitem__(old_cookie)
        try:
            for new_cookie in cookies.split(';'):
                name, value = new_cookie.split('=', 1)
                self._session.cookies[name] = value
        except ValueError as e:
            util.log('Cookies given is invalid, please try again | {}'.format(e), error=True)
        return self.login(self.username, self.password, post_key=self.post_key)

    def _get_post_key_from_pixiv(self):
        util.log('Sending request to retrieve post key ...')
        try:
            pixiv_login_page = util.req(type=self._post_key_req_type, session=self._session, url=self._post_key_url)
            res = re.search(r'post_key" value="(.*?)"', pixiv_login_page.text)
            post_key = res.group(1)
            util.log('Post key successfully retrieved: {post_key}'.format(post_key=post_key))
            return post_key
        except (ReqException, AttributeError) as e:
            util.log(str(e), error=True, save=True)
            raise PostKeyError('Failed to find post key')

    def login(self, username, password, post_key=None):
        """Used to attempt log into pixiv.net

        **Parameters**
        :param post_key:
        :param str username: username of your pixiv account
        :param str password: password of your pixiv account


        **Returns**
        :return: a Session Object which used to login pixiv.net
        :rtype: requests.Session

        **Raises**
        :raises LoginError: if login fails

        """
        self.password = password
        self.username = username

        retry = False
        try:
            if post_key is None:
                retry = True
                post_key = self._get_post_key_from_pixiv()

            self.post_key = post_key

            data = {
                'pixiv_id': username,
                'password': password,
                'post_key': post_key
            }
            util.log('Sending request to attempt login ...')
            respond = util.req(type='post', session=self._session, url=self._login_url, data=data)
            util.log('Login request successfully sent to Pixiv as [{username}]'.format(username=username), inform=True)
            return self._session
        except ReqException as e:
            util.log(str(e), error=True, save=True)
            if retry:
                raise ValueError('Failed login with cookies, please try again')
            util.log('login failed, please enter cookies manually', inform=True)
            self.relogin_with_cookies()


class SearchPage:
    """Representing the search page in pixiv.net

    **Functions**
    :func search: Used to search in pixiv.net

    """
    _search_url = 'https://www.pixiv.net/search.php?'
    _search_popularity_postfix = u'users入り'
    _search_regex = r'(\d{8})_p\d'

    def __init__(self, user=None):
        self._user = user
        self._session = user.session if user != None else None
        self._logged = user != None

    def _set_general_params(self, type, dimension, match, order, mode):
        params = dict()
        if type:  # default match all type
            params['type'] = type

        if dimension:  # default match all ratios
            if dimension == 'horizontal':
                params['ratio'] = '0.5'
            elif dimension == 'vertical':
                params['ratio'] = '-0.5'
            elif dimension == 'square':
                params['ratio'] = '0'
            else:
                raise SearchError('Invalid dimension given:', dimension)

        if match:  # default match if contain tags
            if match == 'strict_tag':  # specified tags only
                params['s_mode'] = 's_tag_full'
            elif match == 'loose':
                params['s_mode'] = 's_tc'
            else:
                raise SearchError('Invalid mode given:', mode)

        if order:
            if order == 'date_desc':
                params['order'] = 'date_d'
            elif order == 'date_asc':
                params['order'] = 'date'
            else:
                raise SearchError('Invalid order given:', order)

        if mode:
            mode = mode.lower()
            params['mode'] = mode
            if mode == 'r18':
                if not self._user:
                    raise SearchError('Please login before searching for r18 content')
                if not self._user.r18:
                    self._user.r18 = True

        return params

    def _search_all_popularities_in_list(self, params, keyword, limit):
        ids = []
        total_limit = limit
        for popularity in settings.SEARCH_POPULARITY_LIST:
            ids += self._search(params=params, keyword=keyword, limit=limit, popularity=popularity)
            if total_limit:
                num_of_ids_sofar = len(ids)
                if num_of_ids_sofar > total_limit:
                    ids = util.trim_to_limit(ids, total_limit)
                    break
                else:
                    limit = total_limit - num_of_ids_sofar
        return ids

    def search(self, keyword, limit=None, type=None, dimension=None, match=None, popularity=None, order='date_desc',
               mode=None):
        """Used to search in pixiv.net

        **Parameters**
        :param keyword:
            a space separated of tags, used for search
        :type keyword:
             str

        :param limit:
            number of artworks is trimmed to this number if too many, may not be enough
        :type limit:
             int or None(default)

        :param type:
            type of artworks,
            'illust' | 'manga', default any
        :type type:
             str or None(default)

        :param dimension:
            dimension of the artworks, 'vertical' | 'horizontal' | 'square', default any
        :type dimension:
             str or None(default)

        :param match:
            define the way of matching artworks with a artwork,
            'strict_tag' matches when any keyword is same as a tag in the artwork
            'loose' matches when any keyword appears in title, description or tags of the artwork
            default matches when any keyword is part of a tag of the artwork
        :type match:
             str or None(default)

        :param popularity:
            this is based on a pixiv search trick to return popular results for non-premium users,
            eg, pixiv automatically adds a 1000users入り tag when a artwork has 1000 likes
            when popularity is given, the str ' ' + popularity + 'users入り' is added to keyword string,
            common popularity of 100, 500, 1000, 5000, 10000, 20000 is strongly suggested, since pixiv does
            not add tag for random likes such as 342users入り
            when str 'popular' is given, it will search for all results with users入り tag in [20000, 10000, 5000, 1000, 500]
            note that 'popular' is the only string accepted
        :type popularity:
            int or str or None(default)

        :param mode:
            'safe': no r18 content
            'r18': has r18 content, if user's r18 is not turn on, it will turn it on before search
            default: both, by user account settings
        :type mode:
            str or None

        **Returns**
        :return: a list of Artwork Object
        :rtype: python list


        **Raises**
        :raises SearchError: if invalid order, mode or dimension is given


        **See Also**
        :class: items.Artwork

        """

        if not self._logged:
            util.log('Search without login may results in incomplete data', warn=True, save=True)

        # for recording
        start = time.time()

        # setting parameters
        params = self._set_general_params(type=type, dimension=dimension, match=match, order=order, mode=mode)

        if not keyword:
            keyword = ''

        # search starts
        if popularity == 'popular':
            ids = self._search_all_popularities_in_list(params=params, keyword=keyword, limit=limit)
        else:
            ids = self._search(params=params, keyword=keyword, limit=limit, popularity=popularity)

        # log ids found
        util.log('Found', str(len(ids)), 'ids for', keyword, 'in', str(time.time() - start) + 's')

        # build artworks from ids
        artworks = util.generate_artworks_from_ids(ids)

        return artworks

    def _search(self, params, keyword, popularity, limit):
        curr_page = 1
        ids_sofar = []
        while True:
            # get a page's ids
            params['p'] = curr_page
            params['word'] = str(keyword)
            if popularity != None:
                params['word'] += ' ' + str(popularity) + self._search_popularity_postfix
            util.log('Searching id for params:', params, 'at page:', curr_page)
            try:
                err_msg = 'Failed getting ids from params ' + str(params) + ' page: ' + str(curr_page)
                results = util.req(type='get', session=self._session, url=self._search_url, params=params,
                                   err_msg=err_msg, log_req=False)
            except ReqException as e:
                util.log(str(e), error=True, save=True)
                if curr_page == 1:
                    util.log('Theres no result found for input', inform=True, save=True)
                else:
                    util.log('End of search at page: ' + str(curr_page), inform=True, save=True)
                return ids_sofar

            ids = re.findall(self._search_regex, results.text)

            # set length of old ids and new ids,
            # use later to check if reached end of all pages
            old_len = len(ids_sofar)
            ids_sofar += ids
            ids_sofar = list(set(ids_sofar))
            new_len = len(ids_sofar)

            # if limit is specified, check if reached limited number of items
            if limit != None:
                if limit == new_len:
                    return ids_sofar
                elif limit < new_len:
                    return util.trim_to_limit(ids_sofar, limit=limit)
                # limit has not reached

            # now check if any new items is added
            if old_len == new_len:  # if no new item added, end of search pages
                if limit != None:  # if limit is specified, it means search ended without meeting user's limit
                    util.log('Search did not return enough items for limit:', new_len, '<', limit, inform=True,
                             save=True)
                return ids_sofar

            # search next page
            curr_page += 1


class RankingPage:
    """Representing ranking page in pixiv.net

    **Functions**
    :func rank: used to get artworks in rank page in pixiv.net

    """

    url = 'https://www.pixiv.net/ranking.php?'

    def __init__(self, user=None):
        self._user = user
        self._session = user.session if user != None else None
        self._logged = user != None

    def _check_inputs(self, content, type, mode):
        if content == 'illust':
            allowed = ['daily', 'weekly', 'monthly', 'rookie']
            if type not in allowed:
                raise RankError('Illust content is only available for type in', allowed)
        if mode == 'r18':
            if self._user == None:
                raise RankError('Please login before retrieving r18 rankings')
            allowed = ['daily', 'weekly', 'male', 'female']
            if type not in allowed:
                raise RankError('R18 mode is only available for type in', allowed)

    def _set_general_params(self, content, date, mode, type):
        params = dict()

        params['format'] = 'json'
        params['mode'] = type

        if content:
            params['content'] = content

        if date:
            if not isinstance(date, str):  # then it has to be datetime.datetime
                date = format(date, '%Y%m%d')
            params['date'] = date

        if mode == 'r18':
            params['mode'] += '_r18'

        return params

    def _rank(self, params, limit):
        ids = []
        page_num = 0
        # exception_count = 0
        while True:
            page_num += 1
            params['p'] = page_num
            try:
                res = util.req(type='get', session=self._session, url=self.url, params=params)
                res = util.json_loads(res.content)
            except (ReqException, json.JSONDecodeError) as e:
                util.log(str(e), error=True, save=True)
                util.log('End of rank at page:', page_num, inform=True, save=True)
                break
            if 'error' in res:
                util.log('End of page while searching', str(params) + '. Finished')
                break
            else:
                ids += [content['illust_id'] for content in res['contents']]

            # check if number of ids reached requirement
            if limit:
                num_of_ids_found = len(ids)
                if limit == num_of_ids_found:
                    break
                elif limit < num_of_ids_found:
                    ids = util.trim_to_limit(ids, limit)
                    break

        return ids

    def rank(self, type='daily', limit=None, date=None, content='illust', mode='safe'):
        """Used to get artworks from pixiv ranking page

        **Parameters**
        :param type:
            type of ranking as in pixiv.net,
            'daily' | 'weekly' | 'monthly' | 'rookie' | 'original' | 'male' | 'female', default daily
        :type type:
            str

        :param limit:
            number of artworks to return, may not be enough, default all
        :type limit:
            int or None

        :param date:
            the date when ranking occur,
            if string given it must be in 'yyyymmdd' format
            eg. given '20190423' and mode daily will return the daily ranking of pixiv on 2019 April 23
            eg. given '20190312' and mode monthly will return the monthly ranking from 2019 Feb 12 to 2019 March 12
            default today
        :type date:
            Datetime or str or None

        :param content:
            type of artwork to return,
            'illust' | 'manga', default 'illust'
        :type content:
            str

        :param mode:
            type of search to use, this needs login
            'safe': no r18 content
            'r18': has r18 content
            default: 'safe'
        :type mode:
            str

        **Returns**
        :return: a list of artworks
        :rtype: list

        """

        # some combinations are not allowed
        self._check_inputs(mode=mode, content=content, type=type)

        # set paramters
        params = self._set_general_params(content=content, date=date, mode=mode, type=type)

        # rank starts
        ids = self._rank(params=params, limit=limit)

        # if limit is specified, check if met
        if limit:
            num_of_ids_found = len(ids)
            if num_of_ids_found < limit:
                util.log('Items found in ranking is less than requirement:', num_of_ids_found, '<', limit, inform=True)

        # log results
        util.log('Done. Total ids found:', len(ids), inform=True)

        # build artwork objects from ids found
        artworks = util.generate_artworks_from_ids(ids)

        return artworks
