
"""
This module contains utilities/tools for pikax

:func log: print according to parameters and settings
:func req: attempt to send network requests using requests lib and returns the result
:func json_loads: given string or bytes, loads and return its json using standard lib
:func generate_artworks_from_ids: returns lists of artworks given list of ids using multiprocessing/multithreading
:func trim_to_limit: returns a trimmed list if items if length exceeded limit given
:func clean_filename: returns the given string after removing no allowed characters
:func print_json: print json in formatted way, used for debug

"""
import sys, json, requests, os, time, math, re
import multiprocessing
from multiprocessing import Process, current_process, Manager
from threading import Thread

from . import settings
from .exceptions import ReqException
from .items import Artwork

sls = os.linesep

_log_type = settings.LOG_TYPE
_std_enabled = _log_type.find('std') != -1
_inform_enabled = _log_type.find('inform') != -1
_save_enabled = _log_type.find('save') != -1
_warn_enabled = _log_type.find('warn') != -1


__all__ = ['log', 'req', 'json_loads', 'generate_artworks_from_ids', 'trim_to_limit', 'multiprocessing_', 'clean_filename', 'print_json', 'read_only_attrs']


def log(*objects, sep=' ', end='\n', file=sys.stdout, flush=True, start='', type='', inform=False, save=False, error=False, warn=False):
    """Print according to params and settings.py

    **Description**
    settings.py's LOG_TYPE controls the overall behaviour of this function
    eg. whether each type of log should be available
    caller code controls the type of log
    eg. whether the strings send to log should be type of inform
    This function copied all params of python's print function, except flush is set to True,
    and some custom parameters as shown below

    **Parameters**
    :param start:
        the string to print at the start, preceeding all other string, including inform & save 's prefix
    :type start:
        string

    :param inform:
        if this is True, a prefix ' >>>' is added at the front of the strings given, default False
    :type inform:
        boolean

    :param error:
        if this is True, a prefix ' !!!' is added at the front of the strings given, default False
    :type error:
        boolean

    :param save:
        if this is True, the strings given is also saved to LOG_FILE as specified in settings.py, default False
    :type save:
        boolean


    """
    global _std_enabled, _inform_enabled, _save_enabled, _warn_enabled
    if _inform_enabled and inform:
        print(start, '>>>', *objects, sep=sep, end=end, file=file, flush=flush)
    if _save_enabled and save:
        print(start, *objects, sep=sep, end=end, file=open(settings.LOG_FILE, 'a'), flush=False)
    if _inform_enabled and error:
        print(start, '!!!', *objects, sep=sep, end=end, file=file, flush=flush)
    if _warn_enabled and warn:
        print(start, '###', *objects, sep=sep, end=end, file=file, flush=flush)
    if _std_enabled and not (inform or save or error or warn):
        print(start, *objects, sep=sep, end=end, file=file, flush=flush)

# send request using requests, raise ReqException if fails all retries
def req(url, type='get', session=None, params=None, data=None, headers=settings.DEFAULT_HEADERS, timeout=settings.TIMEOUT, err_msg=None, log_req=True, verify=True, retries=settings.MAX_RETRIES_FOR_REQUEST):
    """Send requests according to given paramters using requests library

    **Description**
    This function send request using requests library,
    however its parameters does not accepts all paramters as in requests.get/post
    and some custom paramters is added as shown below

    **Parameters**
    :param url:
        the url used for requesting
    :type url:
        string

    :param type:
        the type of requests to send, given string is converted to uppercase before checking, default get
    :type type:
        string

    :param session:
        if this is given, session.get/post is used instead of requests.get/post, default None
    :type session:
        requests.Session

    :param params:
        the paramters send along request, default None
    :type params:
        same as params in requests library

    :param data:
        the data send along when post method is used, default None
    :type data:
        same as data in requests library

    :param headers:
        the headers send along when requesting, default None
    :type headers:
        same as headers in requests library

    :param timeout:
        time out used when send requests, in seconds, default use settings.TIMEOUT
    :type timeout:
        int

    :param err_msg:
        the error message used when requests.exceptions.RequestException is raised during requesting
    :type err_msg:
        string

    :param log_req:
        specify whether to log the details of this request, default True
    :type log_req:
        boolean

    :param verify:
        specify whether to verify the server when sending requests, useful for accessing server blocked
        due to vulerability issue
    :type verify:
        boolean

    :param retries:
        number of retries if request fails, if not given, settings.MAX_RETRIES_FOR_REQUEST is used
    :type retries:
        int


    **Returns**
    :return: respond of the request
    :rtype: requests.Response Object


    **Raises**
    :raises ReqException: if all retries fails or invalid type is given

    """
    type = type.upper()
    curr_retries = 0
    while curr_retries < retries:
        if log_req:
            log(type + ':', str(url), 'with params:', str(params), end='')
        try:

            # try send request according to parameters
            if session:
                if type == 'GET':
                    res = session.get(url=url, headers=headers, params=params, timeout=timeout, verify=verify)
                elif type == 'POST':
                    res = session.post(url=url, headers=headers, params=params, timeout=timeout, verify=verify, data=data)
                else:
                    raise ReqException('Request type error:', type)
            else:
                if type == 'GET':
                    res = requests.get(url=url, headers=headers, params=params, timeout=timeout, verify=verify)
                elif type == 'POST':
                    res = requests.post(url=url, headers=headers, params=params, timeout=timeout, verify=verify, data=data)
                else:
                    raise ReqException('Request type error:', type)

            if log_req:
                log(res.status_code)

            # check if request result is normal
            if res:
                if res.status_code < 400:
                    return res
                else:
                    log('Status code error:', res.status_code, 'retries:', curr_retries, save=True)
            else:
                log('Requests returned Falsey, retries:', curr_retries, save=True)
        except requests.exceptions.Timeout as e:
            log(type, url, params, 'Time Out:', curr_retries, save=True)
            log('Reason:', str(e), save=True, inform=True)
        except requests.exceptions.RequestException as e:
            if err_msg:
                log('RequestException:', err_msg, save=True)
            else:
                log(settings.DEFAULT_REQUEST_ERROR_MSG.format(type=type), save=True)
            log('Reason:', str(e), 'Retries:', curr_retries, save=True)

        curr_retries += 1
        time.sleep(0.5) # dont request again too fast

    # if still fails after all retries
    exception_msg = str(type) + ' failed: ' + str(url) + ' params: ' + str(params)
    raise ReqException(exception_msg)


# attempt to decode given json, raise JSONDecodeError if fails
def json_loads(text, encoding='utf-8'):
    return json.loads(text, encoding=encoding)


def _generate_small_list_of_artworks(ids, artworks):
    artworks += [Artwork.factory(id) for id in ids]

# return a list of artworks given a list of ids, using pool
def generate_artworks_from_ids(ids, limit=None):
    start = time.time()
    log('Generating Artwork objects ... ', start='\r\n', inform=True)
    if limit:
        ids = trim_to_limit(ids, limit=limit)

    artworks = Manager().list()
    multiprocessing_(items=ids, small_list_executor=_generate_small_list_of_artworks, results_saver=artworks)
    log('Done. Time Taken: ' + str(time.time() - start) + 's', inform=True)
    total = len(artworks)
    log('Total Expected:', total, inform=True)
    artworks = [artwork for artwork in artworks if artwork is not None]
    success = len(artworks)
    log('Failed:', total - success, inform=True)
    log('Success:', success, inform=True )
    return artworks

# trim the given items length to given limit
def trim_to_limit(items, limit):
    if items:
        if limit:
            num_of_items = len(items)
            if limit < num_of_items:
                items = items[:limit]
                log('Trimmed', num_of_items, 'items =>', limit, 'items', inform=True)
            else:
                log('Number of items are less than limit:', num_of_items, '<', limit, inform=True, save=True)
    else:
        log('Error, items is false', error=True, save=True)
    return items

# remove invalid file name characters for windows
def clean_filename(string):
    return re.sub(r'[:<>"\/|?*]', '', str(string))

# used for tesing
def print_json(json_obj):
    print(json.dumps(json_obj, indent=4, ensure_ascii=False))

def _multithreading_(items, small_list_executor, results_saver=None):
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
        threads.append(Thread(target=small_list_executor, args=(items_for_this_thread, results_saver), daemon=True))
    log('  |->',current_process().name, '=>', len(threads), 'threads =>', num_of_items, 'items', inform=True)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


# breaks the given items into small lists in different process and threads,
# pass these small lists to small_list_executor
# results_saver is used to save results if any
# raise ValueError if num of max threads specified in settings is < 1
def multiprocessing_(items, small_list_executor, results_saver=None):
    log('Starting multiprocessing...', start='\r\n', inform=True)
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
        processes.append(Process(target=_multithreading_, args=(items_for_this_process, small_list_executor, results_saver), daemon=True))
    log('|--', current_process().name, '=>', len(processes), 'processes =>', num_of_items, 'items', inform=True)
    for process in processes:
        process.start()
    for process in processes:
        process.join()
