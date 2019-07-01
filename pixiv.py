# -*- coding: utf-8 -*-

import requests, time, itertools
import re, sys, os
from util import log
import multiprocessing
from multiprocessing import Pool as ThreadPool
from pages import LoginPage, SearchPage
from items import Artwork

sys.stdout.reconfigure(encoding='utf-8')

def parallel_download(tuple_of_session_folder_id):
    session = tuple_of_session_folder_id[0]
    folder = tuple_of_session_folder_id[1]
    id = tuple_of_session_folder_id[2]
    ArtworkPage(session, id).download_original_pic(folder)


class Pixiv:
    headers = {
        'referer': 'https://www.pixiv.net/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }

    def __init__(self, username, password):
        self.login_page = LoginPage()
        self.session = self.login_page.login(username, password)
        self.search_page = SearchPage(self.session)


        """
        keyword: string to search
        type: manga | illust | ugoira | default any
        dimension: vertical | horizontal | square | default any
        mode: strict_tag | loose | default tag contains
        popularity: a number, add after search keyword as: number users入り | default date descending
        page: which page of the search results to crawl | default 1

        return a list of ArtWork object
        """
    def search(self, keyword="", type="", dimension="", mode="", popularity="", page=1):
        start = time.time()
        log('Generating Artwork objects ... ', end='')
        ids = self.search_page.get_ids(keyword=keyword, type=type, dimension=dimension, mode=mode, popularity=popularity, page=page)
        pool = ThreadPool(8)
        sessions = itertools.repeat(self.session)
        artworks = []
        try:
            artworks = pool.imap_unordered(Artwork.factory, zip(sessions, ids))
        except multiprocessing.ProcessError as e:
            pool.terminate()
            log('Error:', str(e))
        finally:
            pool.close()
            pool.join()
            log('done', time.time() - start, 's')

        results = {}
        results['items'] = artworks
        results['folder'] = '#{keyword}-{type}-{dimension}-{mode}-{popularity}-{page}'.format(keyword=keyword, type=type, dimension=dimension, mode=mode, popularity=popularity, page=page)
        return results
        # results['group_by'] = 'default'

    def download(self, data, folder="", group_by=""): # group by is not yet implement
        start = time.time()
        if not folder:
            folder = data['folder']
        if not os.path.exists(folder):
            os.mkdir(folder)
        folders = itertools.repeat(folder)
        pool = ThreadPool(8)
        try:
            res = pool.map(Artwork.downloader, zip(data['items'], folders))
        except multiprocessing.ProcessError as e:
            pool.terminate()
            log('Error:', str(e))
        finally:
            pool.close()
            pool.join()
            log('done', time.time() - start, 's =>', str(folder))
