# -*- coding: utf-8 -*-

import re, os, time, util, threading, settings
from pages import OtherUserPage

__all__ = ['Artwork', 'PixivResult']


# raise ArtworkError if failed to init
class Artwork():
    referer_url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='
    ajax_url = 'https://www.pixiv.net/ajax/illust/'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }

    """
    self.original_url
    self.views
    self.bookmarks
    self.likes
    self.comments
    self.title
    self.author
    """

    def __init__(self, id):
        self.id = str(id)
        self.ajax_url = self.ajax_url + self.id
        try:
            respond = util.req(type='get', url=self.ajax_url, log_req=False)
            image_data = util.json_loads(respond.content)
        except ReqException as e:
            util.log(str(e), type='error save')
            util.log('Failed to init artwork from id:', self.id,  type='inform save')
            raise ArtworkError()

        self.original_url = image_data['body']['urls']['original'] or None
        self.views = image_data['body']['viewCount'] or None
        self.bookmarks = image_data['body']['bookmarkCount'] or None
        self.likes = image_data['body']['likeCount'] or None
        self.comments = image_data['body']['commentCount'] or None
        self.title = image_data['body']['illustTitle'] or None
        self.author = image_data['body']['userName'] or None
        res = re.search(r'/([\d]+_.*)', self.original_url)
        if res != None:
            self.file_name = str(self.author) + '_' + res.group(1)
        else:
            util.log('failed to look for file_name of id', self.id, type='save inform')
            util.log('string used:', self.original_url, type='save inform')
            self.file_name = 'unknown_' + self.original_url

    # for multiprocessing, return None if failed to init artwork
    def factory(id):
        try:
            return Artwork(id)
        except ArtworkError as e:
            util.log(str(e), type='error save')
            return None

    def download(self, folder="", results_dict=None):
        pic_detail = '[' + str(self.title) + '] by [' + str(self.author) + ']'
        self.file_name = util.clean(self.file_name)
        if folder:
            self.file_name = util.clean(folder) + '/' + self.file_name
        if os.path.isfile(self.file_name):
            if results_dict:
                results_dict['skipped'] += 1
            util.log(pic_detail, 'skipped, reason:', self.file_name, 'exists')
            return
        # pixiv check will check referer
        self.headers['referer'] = self.referer_url + self.id
        try:
            err_msg = pic_detail + ' Failed'
            original_pic_respond = util.req(type='get', url=self.original_url, headers=self.headers, err_msg=err_msg, log_req=False)
            with open(self.file_name, 'wb') as file:
                file.write(original_pic_respond.content)
                util.log(pic_detail + ' OK', type='inform', start=settings.CLEAR_LINE, end='\r')
            if results_dict:
                results_dict['success'] += 1
        except ReqException as e:
            util.log(str(e), type='error save')
            util.log(pic_detail + ' FAILED', type='inform save', start=settings.CLEAR_LINE)
            if results_dict:
                results_dict['failed'] += 1

class PixivResult:
    """
    artworks
    folder
    """
    def __init__(self, artworks, folder=""):
        self.artworks = [artwork for artwork in artworks]
        count = 0
        if folder:
            self.folder = folder
        else:
            while True:
                self.folder = '#PixivResult' + str(count)
                count += 1
                if not os.path.exists(self.folder):
                    break

    def __getitem__(self, index):
        return self.artworks[index]

    def __len__(self):
        return len(self.artworks)

class OtherUser():

    def __init__(self, pixiv_id, session):
        self.id = pixiv_id
        self.user_page = OtherUserPage(self.id, session)
        self.favs_folder = settings.FAV_DOWNLOAD_FOLDER.format(username=self.user_page.username)
        self.mangas_folder = settings.MANGAS_DOWNLOAD_FOLDER.format(username=self.user_page.username)
        self.illusts_folder = settings.ILLUSTS_DOWNLOAD_FOLDER.format(username=self.user_page.username)
        self.fav_artworks = None
        self.manga_artworks = None
        self.illust_artworks = None

    def favs(self, limit=None):
        fav_artworks = util.generate_artworks_from_ids(self.user_page.get_public_fav_ids(limit=limit))
        return PixivResult(fav_artworks, self.favs_folder)

    def mangas(self, limit=None):
        manga_artworks = util.generate_artworks_from_ids(self.user_page.get_manga_ids(limit=limit))
        return PixivResult(manga_artworks, self.mangas_folder)

    def illusts(self, limit=None):
        illust_artworks = util.generate_artworks_from_ids(self.user_page.get_illust_ids(limit=limit))
        return PixivResult(illust_artworks, self.illusts_folder)
