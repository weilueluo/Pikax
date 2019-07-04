


import sys, json, settings, requests, threading, atexit, os


sls = os.linesep
"""
Statistics
"""
failed_requests = dict()
duplicates = dict()
saved = []

dup_lock = threading.Lock()
saved_lock = threading.Lock()

# def inc_saved(text):
#     global saved, saved_lock
#     with saved_lock:
#         saved.append(text)
#
# def inc_dup(key):
#     global duplicates, dup_lock
#     with dup_lock:
#         if key in duplicates:
#             duplicates[key] += 1
#         else:
#             duplicates[key] = 1

def log(*objects, sep=' ', end='\n', file=sys.stdout, flush=True):
    print(*objects, sep=sep, end=end, file=file, flush=flush)

# not working
# def when_exiting():
#     global failed_requests, duplicates, saved
#     log('Exiting, recording statistics')
#     num_of_failed_req = str(len(failed_requests))
#     num_of_dup = str(len(duplicates))
#     num_of_saved = str(len(saved))
#     log('Failed Requests:', num_of_failed_req)
#     log('Duplicates:', num_of_dup)
#     log('Saved:', num_of_saved)
#     with open('log.txt', 'a') as logger:
#         logger.write('=' * 50 + sls)
#         logger.write('Failed Requests:' + num_of_failed_req + sls)
#         logger.write('Duplicates:' + num_of_dup + sls)
#         logger.write('Saved:' + num_of_saved + sls)
#         logger.write(json.dumps(failed_requests, ensure_ascii=False, indent=4) + sls)
#         logger.write(json.dumps(failed_requests, ensure_ascii=False, indent=4) + sls)
#         log('Done')

# atexit.register(when_exiting) # errorous in multithreading, call mannully

get_req_lock = threading.Lock()

def get_req(url, params=None, headers=settings.DEFAULT_HEADERS, timeout=settings.TIMEOUT, exception_msg=None, log_req=True):
    if log_req:
        log('Requesting:', str(url), 'with:', str(params))
    retries = 0
    while retries < 3:
        try:
            res = requests.get(url=url, headers=headers, params=params, timeout=timeout)
            if res.status_code >= 400:
                log('Status code error:', res.status_code, retries)
                retries += 1
            else:
                return res
        except requests.exceptions.Timeout as e:
            retries += 1
            log('Time out:', retries, str(e))
        except requests.exceptions.RequestException as e:
            retries += 1
            if exception_msg:
                log(exception_msg)
            else:
                log('Exception while requesting')
            log('Reason:', str(e), 'Retries:', retries)
    with get_req_lock:
        global failed_requests
        if url in failed_requests:
            failed_requests[url] += 1
        else:
            failed_requests[url] = 1
    return None

def json_loads(text, encoding='utf-8'):
    try:
        return json.loads(text, encoding=encoding)
    except json.JSONDecodeError as e:
        log('Error while turning text to json')
        log('Reason:', str(e))
        return None
