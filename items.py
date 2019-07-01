# -*- coding: utf-8 -*-

import requests, re, os, json, time
from util import log


class Artwork():
    referer_url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='
    ajax_url = 'https://www.pixiv.net/ajax/illust/'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }

    def __init__(self, session, id):
        self.session = session
        self.id = str(id)
        self.ajax_url = self.ajax_url + self.id
        tries = 0
        while tries < 3:
            tries += 1
            try:
                respond = self.session.get(self.ajax_url, headers=self.headers)
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
                log('failed artwork init:', tries, str(e))

    # for multiprocessing
    def factory(zipped_var_tuple):
        session = zipped_var_tuple[0]
        id = zipped_var_tuple[1]
        return Artwork(session, id)

    # for multiprocessing
    def downloader(zipped_var_tuple):
        artwork = zipped_var_tuple[0]
        folder = zipped_var_tuple[1]
        artwork.download(folder=folder)

    # proxies = []
    # def get_proxy():
    #     if Artwork.proxies:
    #         if len(Artwork.proxies)
    #     proxy_url = 'https://gimmeproxy.com/api/getProxy?anonymityLevel=1&country=JP&anonymityLevel=1'
    #     proxy_respond = requests.get(proxy_url, headers=self.headers)
    #     proxy_dict = json.loads(proxy_respond)
    #     ip = proxy_dict['ip']
    #     port = proxy_dict['port']
    #     protocol = proxy_dict['type']
    #     proxies = {protocol: ip + ':' + port}

    def download(self, folder=""):
        if folder:
            self.file_name = folder + '/' + self.file_name
        if os.path.isfile(self.file_name):
            log(self.file_name, 'exists, skipped')
            return
        # pixiv check will check referer
        self.headers['referer'] = self.referer_url + self.id
        count = 0
        while count < 3:
            try:
                count += 1
                original_pic_respond = self.session.get(self.original_url, headers=self.headers)
                if original_pic_respond.status_code < 400:
                    with open(self.file_name, 'wb') as file:
                        file.write(original_pic_respond.content)
                    log('Original image <', self.title, '> by <', self.author, '> OK')
                    break
                else:
                    log('Failed:', original_pic_respond.status_code, count, 'id:', self.id)
            except requests.exceptions.RequestException as e:
                log('Original image <', self.title, '> by <', self.author, '>: failed:', count)
                log('Reason:', str(e))
