


import sys, json, settings, requests, os, time, math, re
import multiprocessing
from multiprocessing import Pool as ThreadPool
from items import Artwork
from multiprocessing import Value, Process, current_process
from threading import Thread

sls = os.linesep

_log_type = settings.LOG_TYPE
_std_enabled = True if _log_type.find('std') != -1 else False
_inform_enabled = True if _log_type.find('inform') != -1 else False
_save_enabled = True if _log_type.find('save') != -1 else False

__all__ = ['log', 'req', 'json_loads', 'generate_artworks_from_ids', 'trim_to_limit', 'multiprocessing_', 'clean']


def log(*objects, sep=' ', end='\n', file=sys.stdout, flush=True, start='', type=''):
    global _std_enabled, _inform_enabled, _save_enabled
    if type:
        if _inform_enabled and type.find('inform') != -1:
            print(start, '>>>', *objects, sep=sep, end=end, file=file, flush=flush)
        if _save_enabled and type.find('save') != -1:
            print(start, *objects, sep=sep, end=end, file=open(settings.LOG_FILE, 'a'), flush=flush)
        if _inform_enabled and type.find('error') != -1:
            print(start, '!!!!!', *objects, sep=sep, end=end, file=file, flush=flush)
    elif _std_enabled:
        print(start, *objects, sep=sep, end=end, file=file, flush=flush)

# send request using requests, return None if fails all retries
def req(url, type='get', session=None, params=None, data=None, headers=settings.DEFAULT_HEADERS, timeout=settings.TIMEOUT, err_msg=None, log_req=True, verify=True):
    type = type.upper()
    retries = 0
    while retries < settings.MAX_RETRIES_FOR_REQUEST:
        if log_req:
            log(type + ':', str(url), 'with params:', str(params), end=' ')
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

            if log_req:
                log(res.status_code)

            # check if request result is normal
            if res:
                if res.status_code < 400:
                    return res
                else:
                    log('Status code error:', res.status_code, 'retries:', retries, type='inform save')
            else:
                log('Requests returned Falsey, retries:', retries, type='inform save')
        except requests.exceptions.Timeout as e:
            log(type, url, params, 'Time Out:', retries, type='inform save')
            log('Reason:', str(e), type='inform save')
        except requests.exceptions.RequestException as e:
            if err_msg:
                log('RequestException:', err_msg, type='inform save')
            else:
                log('Exception while', type, type='inform save')
            log('Reason:', str(e), 'Retries:', retries, type='inform save')

        time.sleep(1) # dont request again too fast
        retries += 1

    # if still fails after all retries
    log(type, 'failed:', url, 'params:', str(params), type='error save')
    return None

# attempt to decode given json, return None if fails
def json_loads(text, encoding='utf-8'):
    try:
        return json.loads(text, encoding=encoding)
    except json.JSONDecodeError as e:
        log('Error while turning text to json.', 'Reason:', str(e), type='error save')
        return None

# return a list of artworks given a list of ids, using pool
def generate_artworks_from_ids(ids, limit=None):
    start = time.time()
    log('Generating Artwork objects ... ', start='\r\n', type='inform')
    if limit:
        ids = trim_to_limit(ids, limit=limit)
    pool = ThreadPool(multiprocessing.cpu_count())
    artworks = []
    try:
        artworks = pool.map(Artwork.factory, ids)
    except multiprocessing.ProcessError as e:
        pool.terminate()
        log('Error while generating artwork:', str(e), type='error save')
    finally:
        pool.close()
        pool.join()
        log('Done. Tried creating', len(ids), 'artworks objects in' ,str(time.time() - start) + 's', type='inform')
    return artworks

# trim the given items length to given limit
def trim_to_limit(items, limit):
    if items:
        if limit:
            num_of_items = len(items)
            if limit < num_of_items:
                items = items[:limit]
                log('Trimmed', num_of_items, 'items =>', limit, 'items', type='inform')
            else:
                log('Number of items are less than limit:', num_of_items, '<', limit, type='inform save')
    else:
        log('Error, items is false', type='error save')
    return items

# remove invalid file name characters for windows
def clean(string):
    return re.sub(r'[:<>"\/|?*]', '', str(string))

# used for tesing
def print_json(json_obj):
    print(json.dumps(json_obj, indent=4))

def _multithreading_(items, small_list_executor, results_dict=None):
    threads = []
    num_of_items = len(items)
    num_of_threads = settings.MAX_THREAD_PER_PROCESS
    if num_of_threads == 1:
        num_of_items_per_thread = num_of_items # if num of threads is 1
    elif num_of_threads > 1:
        while num_of_threads > 1:
            num_of_items_per_thread = math.ceil(num_of_items / num_of_threads)
            if num_of_items_per_thread < settings.MIN_ITEMS_PER_THREAD:
                num_of_threads -= 1
                num_of_items_per_thread = num_of_items # for condition not meet in next loop
            else:
                break
    else:
        raise ValueError('number of threads must be at least 1, please check settings.py')

    if num_of_threads > num_of_items:
        num_of_threads = num_of_items

    for thread_count in range(0, num_of_threads):
        start = thread_count * num_of_items_per_thread
        end = (thread_count + 1) * num_of_items_per_thread
        items_for_this_thread = items[start:end]
        threads.append(Thread(target=small_list_executor, args=(items_for_this_thread, results_dict), daemon=True))
    log('  |->',current_process().name, '=>', len(threads), 'threads =>', num_of_items, 'items', type='inform')
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

# breaks the given items into small lists in different process and threads,
# pass these small lists to small_list_executor
# results_dict is used to save results if any
# raise ValueError if num of max threads specified in settings is < 1
def multiprocessing_(items, small_list_executor, results_dict=None):
    log('Starting multiprocessing...', start='\r\n', type='inform')
    start_time = time.time()
    processes = []
    num_of_items = len(items)
    num_of_processes = os.cpu_count()
    while num_of_processes > 1:
        num_of_items_per_process = math.ceil(num_of_items / num_of_processes)
        if num_of_items_per_process < settings.MIN_ITEMS_PER_THREAD:
            num_of_processes -= 1
            num_of_items_per_process = num_of_items # if next condition failed, num_of_processes = 1
        else:
            break

    if num_of_processes > num_of_items:
        num_of_processes = num_of_items

    for process_count in range(0, num_of_processes):
        start = process_count * num_of_items_per_process
        end = (process_count + 1) * num_of_items_per_process
        items_for_this_process = items[start:end]
        processes.append(Process(target=_multithreading_, args=(items_for_this_process, small_list_executor, results_dict), daemon=True))
    log('|--', current_process().name, '=>', len(processes), 'processes =>', num_of_items, 'items', type='inform')
    for process in processes:
        process.start()
    for process in processes:
        process.join()
