
from pikax.pikax import Pikax
from pikax.exceptions import PikaxException
from pikax import settings

import sys

sys.stdout.reconfigure(encoding='utf-8')


popularity_list = [100, 'popular', None]
limit_list = [5, 1000, None]
match_list = ['strict_tag', 'loose', None]
type_list = ['illust', 'manga', None]
dimension_list = ['vertical', 'horizontal', 'square', None]
keyword_list = ['arknights', 'bilibili']
mode_list = ['r18', 'safe', None]
# this may takes 2hrs
def test_search_normal_inputs():
    pikax = Pikax()

    total = len(popularity_list) * len(limit_list) * len(mode_list) * len(type_list) * len(dimension_list) * len(keyword_list)
    curr = 0
    error_list = []
    for popularity in popularity_list:
        for dimension in dimension_list:
            for keyword in keyword_list:
                for limit in limit_list:
                    for mode in mode_list:
                        for type in type_list:
                            for match in match_list:
                                try:
                                    curr += 1
                                    print(curr, '/', total)
                                    pikax.search(keyword=keyword, limit=limit, type=type, dimension=dimension, mode=mode, popularity=popularity, match=match)
                                except PikaxException as e:
                                    error_list.append(str(e) + ' ' + keyword + ' ' + limit + ' ' + type + ' ' + dimension + ' ' + mode + ' ' + popularity + ' ' + match)

    if len(error_list) == 0:
        print('Test OK')
    else:
        for index, error in enumerate(error_list):
            print('#' + str(index), error)

import random
def test_search_random(num_of_tests):
    pikax = Pikax()
    pikax.login(settings.username, settings.password)
    for i in range(0, num_of_tests):
        keyword = random.choice(keyword_list)
        popularity = random.choice(popularity_list)
        limit = random.choice(limit_list)
        mode = random.choice(mode_list)
        type = random.choice(type_list)
        dimension = random.choice(dimension_list)
        match = random.choice(match_list)
        print('#', i + 1, '/', num_of_tests, ':', keyword, mode, type, dimension, popularity, limit, match)
        pikax.search(keyword=keyword, limit=limit, type=type, dimension=dimension, mode=mode, popularity=popularity, match=match)


from datetime import datetime
rank_modes = ['daily', 'weekly', 'monthly', 'rookie', 'original', 'male', 'female', None]
rank_limits = [5, 1000, None]
rank_dates = [datetime(year=2019,month=4,day=23), None]
rank_contents = ['illust', None]
def test_rank_random(num_of_tests):
    pikax = Pikax()
    pikax.login(settings.username, settings.password)
    for i in range(0, num_of_tests):
        mode = random.choice(rank_modes)
        limit = random.choice(rank_limits)
        date = random.choice(rank_dates)
        content = random.choice(rank_contents)
        print('#', i + 1, '/', num_of_tests, ':', date, mode, content, limit)
        try:
            pikax.rank(date=date, mode=mode, content=content, limit=limit)
        except ValueError as e:
            print(str(e))



def test_user():
    pikax = Pikax()
    user = pikax.login(settings.username, settings.password)
    favs = user.bookmarks()
    illusts = user.illusts() # should be 0

    other_user = user.visits(user_id=212801)
    his_favs = other_user.bookmarks(limit=25)
    his_illusts = other_user.illusts(limit=20)
    his_mangas = other_user.mangas()


from pikax.pikax import Pikax, settings
from pikax import util
from bs4 import BeautifulSoup as bs
import re
def test():
    pixiv = Pikax()
    user = pixiv.login(settings.username, settings.password)
    session = user.session

    headers = {
        'referer': 'https://www.pixiv.net/setting_user.php',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }
    url  = 'https://www.pixiv.net/setting_user.php'
    # res = session.post(url, headers=headers, data=form)
    res = session.get(url, headers=headers)
    print(res.status_code)
    print(res.text)
    # tt = re.search(r'name="tt" value="(.*?)"', res.text).group(1)
    # print(tt)
    # form = {
    #     'mode': 'mod',
    #     'tt': tt,
    #     'user_language': 'en',
    #     'r18': 'show',
    #     'r18g': '1',
    #     'submit': 'save'
    # }
    # res = session.post(url, headers=headers, data=form)
    # print(res.status_code)
    # print(res.text)
    # html = bs(res.text, 'html.parser')
    # print(html.prettify())



def  test2():
    pixiv = Pikax()
    user = pixiv.login(settings.username, settings.password)
    print('r18:', user.r18)
    print('r18g:', user.r18g)
    print('lang:', user.lang)
    print('changing...')
    user.r18 = False
    user.r18g = False
    user.lang = 'zh'
    print('r18:', user.r18)
    print('r18g:', user.r18g)
    print('lang:', user.lang)

def main():
    # test_search_normal_inputs()
    test_search_random(5)
    test_rank_random(5)
    test_user()
    # test2()


if __name__ == '__main__':
    main()
