
from pikax.pikax import Pikax
from pikax.exceptions import PikaxException

popularity_list = [100, 'popular', None]
limit_list = [5, 1000, None]
mode_list = ['strict_tag', 'loose', None]
type_list = ['illust', 'manga', None]
dimension_list = ['vertical', 'horizontal', 'square', None]
keyword_list = ['オリジナル', None]
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
                            try:
                                curr += 1
                                print(curr, '/', total)
                                pikax.search(keyword=keyword, limit=limit, type=type, dimension=dimension, mode=mode, popularity=popularity)
                            except PikaxException as e:
                                error_list.append(str(e) + ' ' + keyword + ' ' + limit + ' ' + type + ' ' + dimension + ' ' + mode + ' ' + popularity)

    if len(error_list) == 0:
        print('Test OK')
    else:
        for index, error in enumerate(error_list):
            print('#' + str(index), error)

import random
def test_search_random(num_of_tests):
    pikax = Pikax()
    for i in range(0, num_of_tests):
        keyword = random.choice(keyword_list)
        popularity = random.choice(popularity_list)
        limit = random.choice(limit_list)
        mode = random.choice(mode_list)
        type = random.choice(type_list)
        dimension = random.choice(dimension_list)
        print('#', i + 1, '/', num_of_tests, ':', keyword, mode, type, dimension, popularity, limit)
        pikax.search(keyword=keyword, limit=limit, type=type, dimension=dimension, mode=mode, popularity=popularity)


from datetime import datetime
rank_modes = ['daily', 'weekly', 'monthly', 'rookie', 'original', 'male', 'female', None]
rank_limits = [5, 1000, None]
rank_dates = [datetime(year=2019,month=4,day=23), None]
rank_contents = ['illust', None]
def test_rank_random(num_of_tests):
    pikax = Pikax()
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


from pikax import settings
def test_user():
    pikax = Pikax()
    user = pikax.login(settings.username, settings.password)
    favs = user.bookmarks()
    pikax.download(favs)
    illusts = user.illusts() # should be 0
    pikax.download(illusts)

    other_user = user.visits(user_id=212801)
    his_favs = other_user.bookmarks(limit=25)
    pikax.download(his_favs)
    his_illusts = other_user.illusts(limit=125)
    pikax.download(his_illusts)
    his_mangas = other_user.mangas()
    pikax.download(his_mangas)

def main():
    # test_search_normal_inputs()
    # test_search_random(10)
    # test_rank_random(10)
    # test_user()



if __name__ == '__main__':
    main()
