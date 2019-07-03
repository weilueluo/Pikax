# -*- coding: utf-8 -*-

import requests, re, time
from util import log

# not used, no need to login
class LoginPage:
    post_key_url = 'https://accounts.pixiv.net/login?'
    login_url = 'https://accounts.pixiv.net/api/login?lang=en'
    headers = {
        'referer': 'https://www.pixiv.net/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }

    def __init__(self):
        self.session = requests.Session()
        log('Generated Session')

    def get_post_key_from_pixiv(self):
        log('Sending request to retrieve post key ... ', end='')
        try:
            pixiv_login_page = self.session.get(self.post_key_url, headers=self.headers)
            log(pixiv_login_page.status_code)
        except requests.exceptions.RequestException as e:
            log('Failed:', str(e))
        post_key = re.search(r'post_key" value="(.*?)"', pixiv_login_page.text).group(1)
        if post_key:
            log('post key successfully retrieved:', post_key)
        else:
            log('failed to find post key')
        return post_key

    def login(self, username, password):
        data = {
            'pixiv_id': username,
            'password': password,
            'post_key': self.get_post_key_from_pixiv()
        }
        log('Sending request to attempt login ... ', end='')
        try:
            respond = self.session.post(self.login_url, data=data, headers=self.headers)
        except requests.exceptions.RequestException as e:
            print('Failed:', str(e))
        log(respond.status_code)
        if respond.status_code < 400:
            print('Logged successfully into Pixiv')
            return self.session
        else:
            log('Login Failed')
            return None


class SearchPage:
    search_url = 'https://www.pixiv.net/search.php?'
    search_popularity_postfix = u'users入り'
    search_regex = r'(\d{8})_p0'
    headers = {
        'referer': 'https://www.pixiv.net/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }
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
        log('Start searching for id with keyword:', keyword)
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
            ids = self.get_ids_recusion_helper(params=params, keyword=keyword, max_page=max_page, popularity=popularity)
        else:
            for popularity in self.popularity_list:
                ids.extend(self.get_ids_recusion_helper(params=params, keyword=keyword, max_page=max_page, popularity=popularity))

        ids = set(ids)
        log('Found', str(len(ids)), 'ids for', keyword, 'in', str(time.time() - start) + 's')
        return ids

    def get_ids_recusion_helper(self, params, keyword, popularity, max_page, curr_page=1, ids_sofar=[]):
        if max_page != None and curr_page > max_page:
            return ids_sofar
        try:
            params['p'] = curr_page
            params['word'] = str(keyword) + ' ' + str(popularity) + ' ' + self.search_popularity_postfix
            log('Searching id for params:', params, 'at page:', curr_page)
            results = requests.get(self.search_url, headers=self.headers, params=params)
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
        except requests.exceptions.RequestException as e:
            log('Failed getting ids:', str(e), 'from params', str(params), 'page:', curr_page)


class RankingPage:
    
