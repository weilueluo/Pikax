# -*- coding: utf-8 -*-

import re, os, time, util, threading


class Artwork():
    referer_url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='
    ajax_url = 'https://www.pixiv.net/ajax/illust/'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }
    dup_lock = threading.Lock()
    saved_lock = threading.Lock()

    def __init__(self, id):
        self.id = str(id)
        self.ajax_url = self.ajax_url + self.id
        respond = util.req(type='get', url=self.ajax_url, log_req=False)
        if respond:
            image_data = util.json_loads(respond.content)
        else:
            util.log('Failed to init artwork', type='inform save')
            return
        self.original_url = image_data['body']['urls']['original']
        self.views = image_data['body']['viewCount']
        self.bookmarks = image_data['body']['bookmarkCount']
        self.likes = image_data['body']['likeCount']
        self.comments = image_data['body']['commentCount']
        self.title = image_data['body']['illustTitle']
        self.author = image_data['body']['userName']
        res = re.search(r'/([\d]+_.*)', self.original_url)
        if res == None:
            util.log('failed to look for file_name of id', self.id, type='save inform')
            util.log('string used:', self.original_url, type='save inform')
            self.file_name = 'unknown_' + self.original_url
        else:
            self.file_name = str(self.author) + '_' + res.group(1)
            self.file_name = re.sub(r'[:<>"\/|?*]', '', self.file_name) # remove not allowed chracters as file name in windows
        return

    # for multiprocessing
    def factory(id):
        return Artwork(id)

    # for multiprocessing
    def downloader(zipped_var_tuple):
        artwork = zipped_var_tuple[0]
        folder = zipped_var_tuple[1]
        artwork.download(folder=folder)

    def download(self, folder=""):
        pic_detail = '<' + str(self.title) + '> by <' + str(self.author) + '>'
        if folder:
            self.file_name = folder + '/' + self.file_name
        if os.path.isfile(self.file_name):
            util.log(pic_detail, 'skipped, reason:', self.file_name, 'exists')
            return
        # pixiv check will check referer
        self.headers['referer'] = self.referer_url + self.id
        err_msg = pic_detail + ' Failed'
        original_pic_respond = util.req(type='get', url=self.original_url, headers=self.headers, err_msg=err_msg, log_req=False)
        if original_pic_respond:
            with open(self.file_name, 'wb') as file:
                file.write(original_pic_respond.content)
                util.log(pic_detail, 'OK', type='inform save')

class PixivResult:
    def __init__(self, artworks):
        self.artworks = [artwork for artwork in artworks]
        count = 0
        while True:
            self.folder = 'PixivResult' + str(count)
            count += 1
            if not os.path.exists(self.folder):
                break

    def __getitem__(self, index):
        return self.artworks[index]

    def __len__(self):
        return len(self.artworks)
