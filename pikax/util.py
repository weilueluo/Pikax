"""
This module contains utilities/tools for pikax

:func log: print according to parameters and settings
:func req: attempt to send network requests using requests lib and returns the result
:func json_loads: given string or bytes, loads and return its json using standard lib
:func trim_to_limit: returns a trimmed list if items if length exceeded limit given
:func clean_filename: returns the given string after removing no allowed characters
:func print_json: print json in formatted way, used for debug

"""
import json
import math
import os
import re
import sys
import time

import requests

from . import settings
from .exceptions import ReqException

sls = os.linesep

_std_enabled = settings.LOG_STD
_inform_enabled = settings.LOG_INFORM
_save_enabled = settings.LOG_SAVE
_warn_enabled = settings.LOG_WARN

__all__ = ['log', 'req', 'json_loads', 'trim_to_limit', 'clean_filename', 'print_json']

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def log(*objects, sep=' ', end='\n', file=sys.stdout, flush=True, start='', inform=False, save=False, error=False,
        warn=False, normal=False):
    """Print according to params and settings.py

    **Description**
    settings.py's LOG_TYPE controls the overall behaviour of this function
    eg. whether each rank_type of log should be available
    caller code controls the rank_type of log
    eg. whether the strings send to log should be rank_type of inform
    This function copied all params of python's print function, except flush is set to True,
    and some custom parameters as shown below

    **Parameters**
    :param start:
        the string to print at the start, preceding all other string, including inform & save 's prefix
    :rank_type start:
        string

    :param inform:
        if this is True, a prefix ' >>>' is added at the front of the strings given, default False
    :rank_type inform:
        boolean

    :param error:
        if this is True, a prefix ' !!!' is added at the front of the strings given, default False
    :rank_type error:
        boolean

    :param save:
        if this is True, the strings given is also saved to LOG_FILE as specified in settings.py, default False
    :rank_type save:
        boolean


    """

    if normal:
        print(start, *objects, sep=sep, end=end, file=file, flush=flush)
        return

    global _std_enabled, _inform_enabled, _save_enabled, _warn_enabled
    if _inform_enabled and inform:
        print(start, '>>>', *objects, sep=sep, end=end, file=file, flush=flush)
    if _save_enabled and save:
        print(start, *objects, sep=sep, end=end, file=open(settings.LOG_FILE, 'a', encoding='utf-8'), flush=False)
    if _inform_enabled and error:
        print(start, '!!!', *objects, sep=sep, end=end, file=file, flush=flush)
    if _warn_enabled and warn:
        print(start, '###', *objects, sep=sep, end=end, file=file, flush=flush)
    if _std_enabled and not (inform or save or error or warn):
        print(start, *objects, sep=sep, end=end, file=file, flush=flush)


# send request using requests, raise ReqException if fails all retries
def req(url, req_type='get', session=None, params=None, data=None, headers=settings.DEFAULT_HEADERS,
        timeout=settings.TIMEOUT, err_msg=None, log_req=settings.LOG_REQUEST, retries=settings.MAX_RETRIES_FOR_REQUEST,
        proxies=settings.REQUEST_PROXIES, verify=True):
    """Send requests according to given parameters using requests library

    **Description**
    This function send request using requests library,
    however its parameters does not accepts all parameters as in requests.get/post
    and some custom parameters is added as shown below

    **Parameters**
    :param url:
        the url used for requesting
    :rank_type url:
        string

    :param req_type:
        the rank_type of requests to send, given string is converted to uppercase before checking, default get
    :rank_type req_type:
        string

    :param session:
        if this is given, session.get/post is used instead of requests.get/post, default None
    :rank_type session:
        requests.Session

    :param params:
        the parameters send along request, default None
    :rank_type params:
        same as params in requests library

    :param data:
        the data send along when post method is used, default None
    :rank_type data:
        same as data in requests library

    :param headers:
        the headers send along when requesting, default None
    :rank_type headers:
        same as headers in requests library

    :param timeout:
        time out used when send requests, in seconds, default use settings.TIMEOUT
    :rank_type timeout:
        int

    :param err_msg:
        the error message used when requests.exceptions.RequestException is raised during requesting
    :rank_type err_msg:
        string

    :param log_req:
        specify whether to log the details of this request, default True
    :rank_type log_req:
        boolean

    :param retries:
        number of retries if request fails, if not given, settings.MAX_RETRIES_FOR_REQUEST is used
    :rank_type retries:
        int

    :param proxies:
        Proxies used for sending request, uses REQUEST_PROXIES in settings.py
    :rank_type proxies:
        dict

    :param verify:
        Whether to verify ssl certificate or not



    **Returns**
    :return: respond of the request
    :rtype: requests.Response Object


    **Raises**
    :raises ReqException: if all retries fails or invalid rank_type is given

    """
    req_type = req_type.upper()
    curr_retries = 0
    while curr_retries < retries:
        if log_req:
            log(req_type + ':', str(url), 'with params:', str(params), end='')
        try:
            # try send request according to parameters
            if session:
                if req_type == 'GET':
                    res = session.get(url=url, headers=headers, params=params, timeout=timeout, proxies=proxies,
                                      verify=verify)
                elif req_type == 'POST':
                    res = session.post(url=url, headers=headers, params=params, timeout=timeout, data=data,
                                       proxies=proxies, verify=verify)
                else:
                    raise ReqException('Request req_type error:', req_type)
            else:
                if req_type == 'GET':
                    res = requests.get(url=url, headers=headers, params=params, timeout=timeout, proxies=proxies,
                                       verify=verify)
                elif req_type == 'POST':
                    res = requests.post(url=url, headers=headers, params=params, timeout=timeout, data=data,
                                        proxies=proxies, verify=verify)
                else:
                    raise ReqException('Request req_type error:', req_type)

            if log_req:
                log(res.status_code)

            # check if request result is normal
            if res:
                if res.status_code < 400:
                    if settings.DELAY_PER_REQUEST:
                        time.sleep(int(settings.DELAY_PER_REQUEST))
                    return res
                else:
                    log('Status code error:', res.status_code, 'retries:', curr_retries, save=True)
            else:
                log('Requests returned Falsey, retries:', curr_retries, save=True)
        except requests.exceptions.Timeout as e:
            log(req_type, url, params, 'Time Out:', curr_retries, save=True)
            log('Reason:', str(e), save=True, inform=True)
        except requests.exceptions.RequestException as e:
            if err_msg:
                log('RequestException:', err_msg, save=True, inform=True)
            else:
                log(settings.DEFAULT_REQUEST_ERROR_MSG.format(type=req_type), save=True, inform=True)
            log('Reason:', str(e), 'Retries:', curr_retries, save=True, inform=True)

        curr_retries += 1
        time.sleep(0.5)  # dont retry again too fast

    # if still fails after all retries
    exception_msg = str(req_type) + ' failed: ' + str(url) + ' params: ' + str(params)
    raise ReqException(exception_msg)


# attempt to decode given json, raise JSONDecodeError if fails
def json_loads(text, encoding='utf-8'):
    return json.loads(text, encoding=encoding)


# trim the given items length to given limit
def trim_to_limit(items, limit):
    if items:
        if limit:
            num_of_items = len(items)

            if num_of_items == limit:
                return items

            if num_of_items > limit:
                items = items[:limit]
                log('Trimmed', num_of_items, 'items =>', limit, 'items')
            else:
                log('Number of items are less than limit:', num_of_items, '<', limit, inform=True, save=True)
    return items


# remove invalid file name characters for windows
def clean_filename(string):
    return re.sub(r'[:<>"\\/|?*]', '', str(string))


# used for testing
def print_json(json_obj):
    print(json.dumps(json_obj, indent=4, ensure_ascii=False))


def new_session():
    return requests.Session()


class Printer(object):

    def __init__(self):
        self.is_first_print = True
        self.last_percent = None
        self.last_percent_time_left = None
        self.last_percent_print_time = None
        self.est_time_lefts = [0, 0, 0, 0, 0]
        self.start_time = None
        self.last_printed_line = None

    def print_progress(self, curr, total, msg=None):
        curr_percent = math.floor(curr / total * 100)
        curr_time = time.time()
        if self.is_first_print:
            est_time_left = float("inf")
            self.is_first_print = False
            self.last_percent_time_left = est_time_left
            self.last_percent_print_time = curr_time
            self.start_time = time.time()
        elif self.last_percent == curr_percent:
            est_time_left = self.last_percent_time_left
        else:
            bad_est_time_left = (curr_time - self.last_percent_print_time) / (curr_percent - self.last_percent) * (
                    100 - curr_percent)
            self.est_time_lefts.append(bad_est_time_left)
            self.est_time_lefts = self.est_time_lefts[1:]
            percent_left = 100 - curr_percent
            percent_diff = curr_percent - self.last_percent
            chunk_left = round(percent_left / percent_diff)
            if chunk_left < len(self.est_time_lefts):
                est_time_left = sum(self.est_time_lefts[-chunk_left:]) / chunk_left if chunk_left != 0 else 0.00
            else:
                est_time_left = sum(self.est_time_lefts) / len(self.est_time_lefts)
            self.last_percent_time_left = est_time_left
            self.last_percent_print_time = curr_time

        self.last_percent = curr_percent

        if est_time_left != 0.0:
            progress_text = '{0} / {1} => {2}% | Time Left est. {3:.2f}s'.format(curr, total, curr_percent,
                                                                                 est_time_left)
        else:
            progress_text = '{0} / {1} => {2}% '.format(curr, total, curr_percent)

        if msg:
            progress_text = progress_text + ' | ' + str(msg)

        if self.last_printed_line:
            spaces = len(self.last_printed_line)
        else:
            spaces = 1

        log(progress_text, end='', start=settings.CLEAR_LINE, inform=True)
        self.last_printed_line = progress_text

    def print_done(self, msg=None):
        if msg:
            log(f' [ done ] => {msg}', normal=True)
        else:  # a float, time taken
            if self.is_first_print:
                log(' [ done ]', normal=True)
            else:
                log(' [ done ] => {0:.2f}s'.format(time.time() - self.start_time), normal=True)
        self.is_first_print = True
        self.start_time = None
        self.last_percent = None
        self.last_percent_print_time = None
        self.last_percent_time_left = None
        self.last_printed_line = None
        self.est_time_lefts = [0, 0, 0]


printer = Printer()


def print_progress(curr, total, msg=None):
    global printer
    printer.print_progress(curr, total, msg)


def print_done(msg=None):
    global printer
    printer.print_done(msg)
