import requests,re,sys


sys.stdout.reconfigure(encoding='utf-8')

url = 'https://www.pixiv.net/ajax/illust/74751807'
headers = {
        'referer': 'https://www.pixiv.net/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }

res = requests.get(url, headers=headers)

ids = re.findall(reg, res.text)
print(res.text)
