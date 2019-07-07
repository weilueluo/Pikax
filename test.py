
import requests, re, json, sys, time
sys.stdout.reconfigure(encoding='utf-8')








post_key_url = 'https://accounts.pixiv.net/login?'
login_url = 'https://accounts.pixiv.net/api/login?lang=en'
headers = {
    'referer': 'https://www.pixiv.net/search.php?',
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
    'original_tag': "",
    'lang': 'en',
    'suggestion': "",
    'tag_category': ""
}
time.sleep(2)
# lang: y,
# originalTag: o,
# suggestion: E,
# tagCategory: A

url = 'https://www.pixiv.net/ajax/tags/translation/suggestion'
res = session.post(url=url, headers=headers, params=params)
print(res.text)
# print(re.findall('(\d{8})_p0', res.text))
