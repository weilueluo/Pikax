# -*- coding: utf-8 -*-

import requests, time, json, itertools
import re, sys, os
from util import log
from multiprocessing import Pool as ThreadPool

sys.stdout.reconfigure(encoding='utf-8')

class LoginPage():
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

class SearchPage():
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










class ArtworkPage():
    referer_url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='
    ajax_url = 'https://www.pixiv.net/ajax/illust/'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }




    def __init__(self, session, id):
        self.session = session
        self.id = str(id)
        self.ajax_url = self.ajax_url + self.id
        self.headers['referer'] = self.referer_url + self.id
        log('Getting data from id:', self.id, '... ', end='')
        count = 0
        while count < 3:
            try:
                respond = self.session.get(self.ajax_url, headers=self.headers)
                log('done')
                image_data = json.loads(respond.content)
                self.original_url = image_data['body']['urls']['original']
                self.views = image_data['body']['viewCount']
                self.bookmarks = image_data['body']['bookmarkCount']
                self.likes = image_data['body']['likeCount']
                self.comments = image_data['body']['commentCount']
                self.title = image_data['body']['illustTitle']
                self.author = image_data['body']['userName']
                self.file_name = re.search(r'/([\d]+_p0.*)', self.original_url).group(1)
                return
            except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                count += 1
                log('failed:', count, str(e))


    def download_original_pic(self, folder):
        file_name = folder + '/' + self.file_name
        if os.path.isfile(file_name):
            log(file_name, 'exists, skipped')
            return
        log('Retrieving original image <', self.title, '> by <', self.author, '>', '... ')
        log('Image url:', self.original_url)
        count = 0
        while count < 3:
            try:
                original_pic = self.session.get(self.original_url, headers=self.headers)
                with open(file_name, 'wb') as file:
                    file.write(original_pic.content)
                log('done')
                break
            except requests.exceptions.RequestException as e:
                count += 1
                log('failed', count)
            except Exception as e:
                count += 1
                log('failed unexpectedly', count)


def static_download(tuple_of_session_folder_id):
    download_session = tuple_of_session_folder_id[0]
    download_folder = tuple_of_session_folder_id[1]
    id = tuple_of_session_folder_id[2]
    if not download_folder or not download_session:
        raise Exception('Please set the download folder and session before using this method')
        return
    ArtworkPage(download_session, id).download_original_pic(download_folder)



class Pixiv():
    headers = {
        'referer': 'https://www.pixiv.net/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }

    def __init__(self, username, password):
        self.login_page = LoginPage()
        self.session = self.login_page.login(username, password)
        self.search_page = SearchPage(self.session)

    def search(self, keyword="", type="", dimension="", mode="", popularity="", page=1):
        ids = self.search_page.get_ids(keyword=keyword, type=type, dimension=dimension, mode=mode, popularity=popularity, page=page)
        total = len(ids)
        folder = '#' + str(keyword) + '-' + str(type) + '-' + str(popularity) + '-' + str(dimension) + '-' + str(page)
        if not os.path.exists(folder):
            os.mkdir(folder)


        download_folder = itertools.repeat(folder)
        download_session = itertools.repeat(self.session)
        pool = ThreadPool(8)
        pool.map(static_download, zip(download_session, download_folder, ids))
        pool.close()
        pool.join()

        log('done', '=>', folder)



import settings

if __name__ == '__main__':
    pixiv = Pixiv(settings.username, settings.password)
    pixiv.search(keyword='艦隊これくしょん', popularity=10000, type='illust', page=1)
