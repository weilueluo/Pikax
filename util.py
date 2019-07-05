


import sys, json, settings, requests, os, time
import multiprocessing
from multiprocessing import Pool as ThreadPool
from items import Artwork
from multiprocessing import Value

sys.stdout.reconfigure(encoding='utf-8')
sls = os.linesep

log_type = settings.LOG_TYPE
std_enabled = True if log_type.find('std') != -1 else False
inform_enabled = True if log_type.find('inform') != -1 else False
save_enabled = True if log_type.find('save') != -1 else False

def log(*objects, sep=' ', end='\n', file=sys.stdout, flush=True, start='', type=''):
    global std_enabled, inform_enabled, save_enabled
    if type:
        if inform_enabled and type.find('inform') != -1:
            print(start, '>>>', *objects, sep=sep, end=end, file=file, flush=flush)
        if save_enabled and type.find('save') != -1:
            print(start, *objects, sep=sep, end=end, file=open(settings.LOG_FILE, 'a'), flush=flush)
    elif std_enabled:
        print(start, *objects, sep=sep, end=end, file=file, flush=flush)

def req(url, type='get', session=None, params=None, data=None, headers=settings.DEFAULT_HEADERS, timeout=settings.TIMEOUT, err_msg=None, log_req=True, verify=True):
    type = type.upper()
    if log_req:
        log(type + ':', str(url), 'with:', str(params), end=' ')
    retries = 0
    while retries < 3:
        try:
            # try send request according to parameters
            if session:
                if type == 'GET':
                    res = session.get(url=url, headers=headers, params=params, timeout=timeout, verify=verify)
                elif type == 'POST':
                    res = session.post(url=url, headers=headers, params=params, timeout=timeout, verify=verify, data=data)
                else:
                    log('Request type error:', type, type='inform save')
            else:
                if type == 'GET':
                    res = requests.get(url=url, headers=headers, params=params, timeout=timeout, verify=verify)
                elif type == 'POST':
                    res = requests.post(url=url, headers=headers, params=params, timeout=timeout, verify=verify, data=data)
                else:
                    log('Request type error:', type, type='inform save')
            # check if request is normal
            if res:
                if log_req:
                    log(res.status_code)
                if res.status_code < 400:
                    return res
                else:
                    log('Status code error:', res.status_code, 'retries:', retries, type='inform save')
            else:
                if log_req:
                    log('')
                log('Requests return unexpected result, retries:', retries, type='inform save')
        except requests.exceptions.Timeout as e:
            log(type, 'time out:', retries, str(e), type='inform save')
        except requests.exceptions.RequestException as e:
            if err_msg:
                log(err_msg, type='inform save')
            else:
                log('Exception while', type, type='inform save')
            log('Reason:', str(e), 'Retries:', retries, type='inform save')

        time.sleep(1) # dont request again too fast
        retries += 1
    log(type, 'failed:', url, 'params:', str(params), type='inform save')
    return None

def json_loads(text, encoding='utf-8'):
    try:
        return json.loads(text, encoding=encoding)
    except json.JSONDecodeError as e:
        log('Error while turning text to json.', 'Reason:', str(e), type='inform save')
        return None

def generate_artworks_from_ids(ids):
    start = time.time()
    log('Generating Artwork objects ... ', type='inform')
    pool = ThreadPool(multiprocessing.cpu_count())
    artworks = []
    try:
        artworks = pool.map(Artwork.factory, ids)
    except multiprocessing.ProcessError as e:
        pool.terminate()
        log('Error while generating artwork:', str(e), type='inform save')
    finally:
        pool.close()
        pool.join()
        log('Done. Tried creating', len(ids), 'artworks objects in' ,str(time.time() - start) + 's', type='inform')
    return artworks

def trim_to_limit(items, limit, username):
    if limit:
        num_of_items = len(items)
        if limit < num_of_items:
            items = items[:limit]
            log(username + '\'s favs', num_of_items, '=>', limit, type='inform')
        else:
            log(username + '\'s favs is less than limit:', num_of_favs, '<', limit, type='inform save')
    return items

def init_download_counter(counter_, total_):
    global counter, total
    counter = counter_
    total = total_
