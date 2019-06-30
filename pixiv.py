# -*- coding: utf-8 -*-

import requests, time, itertools
import re, sys, os
from util import log
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
        ids = self.search_page.get_ids(keyword=keyword, type=type, dimension=dimension, mode=mode, popularity=popularity, page=page)
        pool = ThreadPool(4)
        sessions = itertools.repeat(self.session)

        start = time.time()
        results = pool.imap_unordered(Artwork.factory, zip(sessions, ids), chunksize=os.cpu_count())
        pool.close()
        pool.join()
        log('Time taken to generate artworks:', time.time() - start, 's')
        return results


    def download(self, artworks, folder="", group_by="artists"):
        if not os.path.exists(folder):
            os.mkdir(folder)
        pass



import settings

if __name__ == '__main__':
    pixiv = Pixiv(settings.username, settings.password)
    results = pixiv.search(keyword='女の子', popularity=10000, type='illust', page=1)
    print(results)
