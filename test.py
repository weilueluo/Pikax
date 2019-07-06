
import requests, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')




import os
from multiprocessing import Process
from threading import Thread





def f(x):
    sum = 0
    for v in x:
        sum += v
    print(sum)

def multithreading_download(items):
    threads = []
    length = len(items)
    num_of_threads = 4
    if num_of_threads > length:
        num_of_threads = length
    items_for_each_thread = length // num_of_threads  + 1
    for i in range(0, num_of_threads):
        start = items_for_each_thread * i
        end = items_for_each_thread * (i + 1)
        items_for_this_thread = items[start:end]
        print('   ', items_for_this_thread)
        threads.append(Thread(target=f, args=(items_for_this_thread, ), daemon=True))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    arr = [x for x in range(107)]
    length = len(arr)
    num_of_processes = os.cpu_count()
    if num_of_processes > length:
        num_of_processes = length

    processes = []
    items_for_each_processor = length // num_of_processes + 1
    # print('num_of_processes:', num_of_processes)
    for i in range(0, num_of_processes):
        start_pos = items_for_each_processor * i
        end_pos = items_for_each_processor * (i + 1)
        items_for_this_processor = arr[start_pos:end_pos]
        print(items_for_this_processor)
        processes.append(Process(target=multithreading_download, args=(items_for_this_processor, ), daemon=True))

    for process in processes:
        process.start()

    for process in processes:
        process.join()










# post_key_url = 'https://accounts.pixiv.net/login?'
# login_url = 'https://accounts.pixiv.net/api/login?lang=en'
# headers = {
#     'referer': 'https://www.pixiv.net/bookmark.php?id=5594793&rest=show',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
# }
#
# session = requests.Session()
# pixiv_login_page = session.get(url=post_key_url,headers=headers)
# post_key = re.search(r'post_key" value="(.*?)"', pixiv_login_page.text).group(1)
# data = {
#     'pixiv_id': 'restorecyclebin@gmail.com',
#     'password': '123456',
#     'post_key': post_key
# }
# res = session.post(url=login_url, data=data, headers=headers)
# if res.status_code == 200:
#     print('success login')
# else:
#     print('failed login')
#
# params = {
#     'tag': '',
#     'offset': '0',
#     'limit': '1',
#     'rest': 'show'
# }
#
# url = 'https://www.pixiv.net/ajax/user/5594793/illusts/bookmarks?'
# res = session.get(url=url, headers=headers, params=params)
# print(json.dumps(json.loads(res.text, encoding='utf-8'), indent=4, ensure_ascii=False))
# print(res.text)
# print(re.findall('(\d{8})_p0', res.text))
