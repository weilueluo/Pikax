import requests
import sys,re

sys.stdout.reconfigure(encoding='utf-8')

post_key_url = 'https://accounts.pixiv.net/login?'
login_url = 'https://accounts.pixiv.net/api/login?lang=en'
headers = {
    'referer': 'https://www.pixiv.net',
    'user-agent':'PixivIOSApp/7.6.2 (iOS 12.2; iPhone9,1)'
    # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
}

session = requests.Session()
pixiv_login_page = session.get(url=post_key_url,headers=headers)
post_key = re.search(r'post_key" value="(.*?)"', pixiv_login_page.text).group(1)
data = {
    'pixiv_id': 'restorecyclebin@gmail.com',
    'password': '123456',
    'post_key': post_key
}
res = session.post(url=login_url, data=data, headers=headers)
if res.status_code == 200:
    print('success login')
else:
    print('failed login')


url = 'https://www.pixiv.net/touch/ajax/user/bookmarks?'
params = {
    'id': 6662895,
    'type': 'illust',
    'p': 1
}
headers = {
'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
'referer': 'https://www.pixiv.net/bookmark.php?id=6662895',
}

res = session.get(url=url, params=params, headers=headers)
print(res.text)
# import json
#
# res = json.loads(res.content)
# print(json.dumps(res), indent=4, ensure_ascii=False)
