
import requests, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
post_key_url = 'https://accounts.pixiv.net/login?'
login_url = 'https://accounts.pixiv.net/api/login?lang=en'
headers = {
    'referer': 'https://www.pixiv.net/bookmark.php?id=5594793&rest=show',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
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

params = {
    'tag': '',
    'offset': '0',
    'limit': '1',
    'rest': 'show'
}

url = 'https://www.pixiv.net/ajax/user/5594793/illusts/bookmarks?'
res = session.get(url=url, headers=headers, params=params)
print(json.dumps(json.loads(res.text, encoding='utf-8'), indent=4, ensure_ascii=False))
# print(res.text)
# print(re.findall('(\d{8})_p0', res.text))
