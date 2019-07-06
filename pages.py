# -*- coding: utf-8 -*-

import re, time, util, settings, requests

__all__ = ['LoginPage', 'SearchPage', 'RankingPage', 'UserPage']

class LoginPage:
    post_key_url = 'https://accounts.pixiv.net/login?'
    login_url = 'https://accounts.pixiv.net/api/login?lang=en'
    headers = {
        'referer': 'https://accounts.pixiv.net/login',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }
    def __init__(self):
        self.session = requests.Session()

    def get_post_key_from_pixiv(self):
        util.log('Sending request to retrieve post key ... ', end='')
        pixiv_login_page = util.req(type='get', session=self.session, url=self.post_key_url)
        if pixiv_login_page:
            res = re.search(r'post_key" value="(.*?)"', pixiv_login_page.text)
        if res:
            post_key = res.group(1)
            if post_key:
                util.log('post key successfully retrieved:', post_key)
                return post_key
            else:
                util.log('failed to find post key', type='inform save')
        return None

    def login(self, username, password):
        data = {
            'pixiv_id': username,
            'password': password,
            'post_key': self.get_post_key_from_pixiv()
        }
        util.log('Sending request to attempt login ... ')
        respond = util.req(type='post', session=self.session, url=self.login_url, data=data, headers=self.headers)
        if respond:
            util.log('Login successfully into Pixiv as [', username, ']', type='inform')
            return self.session
        else:
            raise LoginError('Login failed. Please check your internet, username and password', type='inform save')


class SearchPage:
    search_url = 'https://www.pixiv.net/search.php?'
    search_popularity_postfix = u'users入り'
    search_regex = r'(\d{8})_p0'
    popularity_list = [500, 1000, 5000, 10000, 20000]

    """
    keyword: string to search
    type: manga | illust | ugoira | default any
    dimension: vertical | horizontal | square | default any
    mode: strict_tag | loose | default tag contains
    popularity: a number, add after search keyword as: number users入り | default date descending
    max_page: how many pages to crawl | default all pages found
    """

    def __init__(self):
        pass

    def get_ids(self, keyword, max_page=None, type=None, dimension=None, mode=None, popularity=None):
        # if max_page is None, it will search all pages
        util.log('Start searching for id with keyword:', keyword)
        start = time.time()
        # setting parameters
        params = dict()
        if type: # default match all type
            params['type'] = type
        if dimension: # default match all ratios
            if dimension == 'horizontal':
                params['ratio'] = '0.5'
            if dimension == 'vertical':
                params['ratio'] = '-0.5'
            if dimension == 'square':
                params['ratio'] = '0'
        if mode: # default match if contain tags
            if mode == 'strict_tag': # specified tags only
                params['s_mode'] = 's_tag_full'
            if mode == 'loose':
                params['s_mode'] = 's_tc'

        # search all ids from pages
        ids = []
        if popularity:
            ids += self.get_ids_recusion_helper(params=params, keyword=keyword, max_page=max_page, popularity=popularity)
        else:
            for popularity in self.popularity_list:
                ids += self.get_ids_recusion_helper(params=params, keyword=keyword, max_page=max_page, popularity=popularity)
        ids = set(ids)
        util.log('Found', str(len(ids)), 'ids for', keyword, 'in', str(time.time() - start) + 's', type='inform')
        return ids

    def get_ids_recusion_helper(self, params, keyword, popularity, max_page, curr_page=1, ids_sofar=[]):
        if max_page != None and curr_page > max_page:
            return ids_sofar
        params['p'] = curr_page
        params['word'] = str(keyword) + ' ' + str(popularity) + ' ' + self.search_popularity_postfix
        util.log('Searching id for params:', params, 'at page:', curr_page)
        err_msg = 'Failed getting ids from params ' + str(params) + ' page: ' + str(curr_page)
        results = util.req(type='get', url=self.search_url, params=params, err_msg=err_msg)
        ids = re.findall(self.search_regex, results.text)
        # checking if any new item is added
        old_len = len(ids_sofar)
        ids_sofar += ids
        ids_sofar = list(set(ids_sofar))
        new_len = len(ids_sofar)
        if old_len == new_len: # if no new item added, end of page
            return ids_sofar
        curr_page += 1
        ids_sofar = self.get_ids_recusion_helper(params=params, keyword=keyword, popularity=popularity, max_page=max_page, curr_page=curr_page, ids_sofar=ids_sofar)
        return ids_sofar


class RankingPage:
    url = 'https://www.pixiv.net/ranking.php?'

    def __init__(self):
        pass

    """
    mode: daily | weekly | monthly | rookie | original | male | female | default daily
    max_page: 1 page = 50 artworks | default all pages
    date: up to which date | default today, format: yyyymmdd
    content: illust | manga | ugoria | default any
    """
    def rank(self, mode='daily', max_page=None, date=None, content=None):
        params = dict()
        params['format'] = 'json'
        params['mode'] = mode
        if date:
            params['date'] = date
        if content:
            params['content'] = content

        util.log('Start searching ranking for mode', mode, '...', type='inform')
        start = time.time()
        ids = []
        if max_page:
            for page_num in range(1, int(max_page) + 1):
                params['p'] = page_num
                res = util.req(type='get', url=self.url, params=params)
                if res:
                    res = util.json_loads(res.content)
                else:
                    continue
                if 'error' in res:
                    util.log('Error while searching', str(params), 'skipped', type='inform save')
                    continue
                else:
                    ids += [content['illust_id'] for content in res['contents']]
        else:
            page_num = 0
            while True:
                page_num += 1
                params['p'] = page_num
                res = util.req(type='get', url=self.url, params=params)
                if res:
                    res = util.json_loads(res.content)
                else:
                    util.log('Error while json loading', type='inform save')
                    continue
                if 'error' in res:
                    util.log('End of page while searching', str(params) + '. Finished')
                    break
                else:
                    ids += [content['illust_id'] for content in res['contents']]
        util.log('Done. Total ids found:', len(ids), type='inform')

        return ids


class UserPage:
    data_url = 'https://www.pixiv.net/ajax/user/{pixiv_id}/illusts/bookmarks?'
    bookmark_url = 'https://www.pixiv.net/bookmark.php?'
    params = {
        'tag': '',
        'offset': '0',
        'limit': '1',
        'rest': 'show'
    }
    """
    self vars:
        data_url
        bookmark_url
        id
        title
        public_fav_ids
    """

    def add_public_fav(self):
        ids_url = self.data_url.format(pixiv_id=self.id, limit=self.total_fav)
        self.params['limit'] = self.total_fav
        ids_data = util.req(type='get', session=self.session, url=ids_url, params=self.params)
        ids_data = util.json_loads(ids_data.content)
        if ids_data:
            self.public_fav_ids = [artwork['id'] for artwork in ids_data['body']['works']]
            self.public_fav_ids_length = len(self.public_fav_ids)
            util.log(self.username + '\'s favs found:', self.public_fav_ids_length, type='inform')
        else:
            util.log('Failed to retrieve ids data from id:', self.id, type='inform save')

    def __init__(self, pixiv_id, session):
        self.public_fav_ids = []
        self.id = pixiv_id
        self.session = session
        req_url = self.data_url.format(pixiv_id=self.id)
        err_msg = 'Error while generating user page, id: ' + str(self.id)
        res = util.req(type='get', session=self.session, url=req_url, params=self.params, err_msg=err_msg)
        if res:
            res_json = util.json_loads(res.text)
            if res_json:
                if not res_json['error']:
                    self.total_fav = res_json['body']['total']
                    title = res_json['body']['extraData']['meta']['title']
                    username = re.search(r'「(.*?)」', title)
                    self.username = username.group(1) if username else title
                    self.add_public_fav()

    def get_public_fav_ids(self, limit=None):
        return util.trim_to_limit(items=self.public_fav_ids, limit=limit, username=self.username)
