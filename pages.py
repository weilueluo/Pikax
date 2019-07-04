# -*- coding: utf-8 -*-

import re, time, util



# not used, no need to login
# class LoginPage:
#     post_key_url = 'https://accounts.pixiv.net/login?'
#     login_url = 'https://accounts.pixiv.net/api/login?lang=en'
#     headers = {
#         'referer': 'https://www.pixiv.net/',
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
#     }
#
#     def __init__(self):
#         self.session = requests.Session()
#         util.log('Generated Session')
#
#     def get_post_key_from_pixiv(self):
#         util.log('Sending request to retrieve post key ... ', end='')
#         try:
#             pixiv_login_page = self.session.get(self.post_key_url, headers=self.headers)
#             util.log(pixiv_login_page.status_code)
#         except requests.exceptions.RequestException as e:
#             util.log('Failed:', str(e))
#         post_key = re.search(r'post_key" value="(.*?)"', pixiv_login_page.text).group(1)
#         if post_key:
#             util.log('post key successfully retrieved:', post_key)
#         else:
#             util.log('failed to find post key')
#         return post_key
#
#     def login(self, username, password):
#         data = {
#             'pixiv_id': username,
#             'password': password,
#             'post_key': self.get_post_key_from_pixiv()
#         }
#         util.log('Sending request to attempt login ... ', end='')
#         try:
#             respond = self.session.post(self.login_url, data=data, headers=self.headers)
#         except requests.exceptions.RequestException as e:
#             util.log('Failed:', str(e))
#         util.log(respond.status_code)
#         if respond.status_code < 400:
#             util.log('Logged successfully into Pixiv')
#             return self.session
#         else:
#             util.log('Login Failed')
#             return None


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
        util.log('Found', str(len(ids)), 'ids for', keyword, 'in', str(time.time() - start) + 's')
        return ids

    def get_ids_recusion_helper(self, params, keyword, popularity, max_page, curr_page=1, ids_sofar=[]):
        if max_page != None and curr_page > max_page:
            return ids_sofar
        params['p'] = curr_page
        params['word'] = str(keyword) + ' ' + str(popularity) + ' ' + self.search_popularity_postfix
        util.log('Searching id for params:', params, 'at page:', curr_page)
        exception_msg = 'Failed getting ids from params ' + str(params) + ' page: ' + str(curr_page)
        results = util.get_req(url=self.search_url, params=params, exception_msg=exception_msg)
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

        util.log('Start ranking for mode', mode, '...')
        start = time.time()
        ids = []
        if max_page:
            for page_num in range(1, int(max_page) + 1):
                params['p'] = page_num
                res = util.get_req(url=self.url, params=params)
                if res:
                    res = util.json_loads(res.content)
                else:
                    continue
                if 'error' in res:
                    util.log('Error while searching', str(params), 'skipped')
                    continue
                else:
                    ids += [content['illust_id'] for content in res['contents']]
        else:
            page_num = 0
            while True:
                page_num += 1
                params['p'] = page_num
                res = util.get_req(url=self.url, params=params)
                if res:
                    res = util.json_loads(res.content)
                else:
                    continue
                if 'error' in res:
                    util.log('End of page while searching', str(params) + '. Finished')
                    break
                else:
                    ids += [content['illust_id'] for content in res['contents']]
        util.log('Done. Total ids found:', len(ids))

        return ids
