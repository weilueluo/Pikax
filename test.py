import json
import requests
from pikax import util

from pikax.items import User

from pikax.pikax import Pikax, settings
from pikax.pages import LoginPage
from pikax.util import print_json
import sys
sys.stdout.reconfigure(encoding='utf-8')


def main():
    # pixiv = Pikax()
    # pixiv.login(settings.username, settings.password)  # 不必要但强烈推荐
    # results = pixiv.rank(limit=20, content='illust', type='daily', mode='safe')
    # pixiv.download(results, folder='#Pixiv_daily_ranking')
    # session = LoginPage().login(settings.username, settings.password)
    # headers = {
    #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    # }
    # res = session.post('https://www.google.com/recaptcha/api2/reload?k=6LfJ0Z0UAAAAANqP-8mvUln2z6mHJwuv5YGtC8xp', headers=headers)
    # print(res.text)
    user = User(settings.username, settings.password)
    # cookies = input('paste cookies:')
    # s = requests.session()
    # for cookie in cookies.split(';'):
    #     name, value = cookie.split('=', 1)
    #     s.cookies[name] = value
    # login_url = 'https://accounts.pixiv.net/api/login?'
    # res = s.get(url='https://www.pixiv.net/touch/ajax/user/self/status')
    # status_json = util.json_loads(res.content)
    # print('login:', status_json['body']['user_status']['is_logged_in'])

if __name__ == '__main__':
    main()
