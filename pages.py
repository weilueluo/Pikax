# -*- coding: utf-8 -*-

import requests, re
from util import log


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

    """
    keyword: string to search
    type: manga | illust | ugoira | default any
    dimension: vertical | horizontal | square | default any
    mode: strict_tag | loose | default tag contains
    popularity: a number, add after search keyword as: number users入り | default date descending
    page: which page of the search results to crawl | default 1
    """

    def __init__(self, session):
        self.session = session

    def get_ids(self, keyword="", type="", dimension="", mode="", popularity="", page=1):
        params = dict()
        if keyword: # default display tags
            popularity = str(popularity) + ' ' + self.search_popularity_postfix
            params['word'] = str(keyword) + ' ' + popularity
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
        params['p'] = page
        log('Searching id for params:', str(params), '...', end=' ')
        try:
            results = self.session.get(self.search_url, headers=self.headers, params=params)
            ids = re.findall(self.search_regex, results.text)
            log('done:', len(ids))
            return set(ids)
        except requests.exceptions.RequestException as e:
            log('Failed:', str(e))
            return None
