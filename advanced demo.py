#!/usr/bin/env python
# coding: utf-8

# In[1]:


from importlib import reload

import pikax.settings as settings
from pikax import util
import pikax
from pikax.api.artwork import Illust
from pikax.api.androidclient import AndroidAPIClient
import multiprocessing as mp
from tqdm import tqdm
import os
import itertools
import requests


settings.LOG_STD = False
settings.LOG_INFORM = False
settings.LOG_WARN = False
settings.LOG_NORMAL = False
settings.MAX_PAGES_PER_ARTWORK = 1
reload(util)


# In[2]:


def worker_proc(fn, queue, stop_item):
    while True:
        item = queue.get()
        if item == stop_item:
            break
        fn(item)


def concurrent_run(fn, inputs, num_workers=4, stop_item=None, name='Unavailable'):
    queue = mp.Queue(1)
    stop_item = stop_item

    workers = []
    for _ in range(num_workers):
        workers.append(mp.Process(target=worker_proc, args=(fn, queue, stop_item)))
    for worker in workers:
        worker.start()

    tqdm_iter = tqdm(inputs, ncols=100, desc=tqdm_desc_pre)
    for input_ in tqdm_iter:
        tqdm_iter.set_description_str(desc=f'{tqdm_desc_pre} {input_[0]}')
        queue.put(input_)
    for _ in workers:
        queue.put(stop_item)
    for worker in workers:
        worker.join()


# In[3]:


def download_id(item):
    id_, path = item
    try:
        illust = Illust(id_)
        illust.config()
        if illust.likes < like_threshold:
            # tqdm_iter.set_description_str(desc=tqdm_desc_pre + f' {illust.title} {illust.likes} < {like_threshold}')
            return
        status, (download_url, headers), filename = next(iter(illust))
        os.makedirs(path, exist_ok=True)
        image_path = os.path.join(path, filename)
        if os.path.exists(image_path):
            # tqdm_iter.set_description_str(desc=tqdm_desc_pre + f' {filename} exists')
            return
        with open(image_path, 'wb') as file:
            with requests.get(download_url, headers=headers, stream=True) as req:
                req.raise_for_status()
                for chunk in req.iter_content(1024):
                    file.write(chunk)
        # tqdm_iter.set_description_str(desc=tqdm_desc_pre + f' {filename} {illust.likes} done')
    except (pikax.exceptions.ArtworkError, requests.RequestException, OSError):
        tqdm.write(f'{id_} failed')


# In[4]:

search_limit = 3000
like_threshold = 50
num_workers = 8
path = 'images_data/data/{name}'
tqdm_desc_pre = 'Download Artworks'


def main():
    search_names = ['黑子的篮球', 'lovelive', '進撃の巨人', '银魂', 'one piece', '十六夜咲夜', '名探偵コナン',
                    '琪露诺', '碧蓝航线', '鬼灭之刃', 'JoJo的奇妙冒险', '龙珠', '游戏王', '芙兰朵露・斯卡蕾特', '少女前线',
                    '晓美焰', '轻音少女', '鹿目圆', '灵梦', '东京喰种']

    client = AndroidAPIClient(settings.username, settings.password)
    names = tqdm(search_names, ncols=75)
    for name in names:
        names.set_description_str(desc=f'Class: {name}')
        ids = client.search(keyword=name, limit=search_limit)
        download_path = path.format(name=name)
        concurrent_run(download_id, list(zip(ids, itertools.repeat(download_path))),
                       num_workers=num_workers,
                       name=name)


# In[5]:

if __name__ == '__main__':
    main()
