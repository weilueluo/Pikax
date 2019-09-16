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


# changed for gui
def log(*objects, sep=' ', end='\n', file=sys.stdout, flush=True, start='', inform=False, save=False, error=False,
        warn=False, normal=False):
    import sys

    line = ''.join(str(item) for item in objects)
    sys.stdout.write(str(start) + line + str(end))


# send request using requests, raise ReqException if fails all retries
def req(url, req_type='get', session=None, params=None, data=None, headers=settings.DEFAULT_HEADERS,
        timeout=settings.TIMEOUT, err_msg=None, log_req=settings.LOG_REQUEST, retries=settings.MAX_RETRIES_FOR_REQUEST,
        proxies=settings.REQUEST_PROXIES):
    """Send requests according to given parameters using requests library

    **Description**
    This function send request using requests library,
    however its parameters does not accepts all parameters as in requests.get/post
    and some custom parameters is added as shown below

    **Parameters**
    :param url:
        the url used for requesting
    :type url:
        string

    :param req_type:
        the type of requests to send, given string is converted to uppercase before checking, default get
    :type req_type:
        string

    :param session:
        if this is given, session.get/post is used instead of requests.get/post, default None
    :type session:
        requests.Session

    :param params:
        the parameters send along request, default None
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

    :param retries:
        number of retries if request fails, if not given, settings.MAX_RETRIES_FOR_REQUEST is used
    :type retries:
        int

    :param proxies:
        Proxies used for sending request, uses REQUEST_PROXIES in settings.py
    :type proxies:
        dict


    **Returns**
    :return: respond of the request
    :rtype: requests.Response Object


    **Raises**
    :raises ReqException: if all retries fails or invalid type is given

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
                    res = session.get(url=url, headers=headers, params=params, timeout=timeout, proxies=proxies)
                elif req_type == 'POST':
                    res = session.post(url=url, headers=headers, params=params, timeout=timeout, data=data,
                                       proxies=proxies)
                else:
                    raise ReqException('Request type error:', req_type)
            else:
                if req_type == 'GET':
                    res = requests.get(url=url, headers=headers, params=params, timeout=timeout, proxies=proxies)
                elif req_type == 'POST':
                    res = requests.post(url=url, headers=headers, params=params, timeout=timeout, data=data,
                                        proxies=proxies)
                else:
                    raise ReqException('Request type error:', req_type)

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
                log('RequestException:', err_msg, save=True)
            else:
                log(settings.DEFAULT_REQUEST_ERROR_MSG.format(type=req_type), save=True)
            log('Reason:', str(e), ' Retries:', curr_retries, save=True)

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


# changed for gui
class Printer(object):

    def __init__(self):
        self.is_first_print = True
        self.last_percent = None
        self.last_percent_time_left = None
        self.last_percent_print_time = None
        self.est_time_lefts = [0, 0, 0]
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

        progress_text = '\n'.join(progress_text.split('|'))
        log(progress_text, end='', start=settings.CLEAR_LINE, inform=True)
        self.last_printed_line = progress_text

    def print_done(self, msg=None):
        if msg:
            if self.is_first_print:
                log(f' [ done ] => {msg}', normal=True)
            else:
                log(' [ done ] => {0:.2f}s \n{msg}'.format(time.time() - self.start_time, msg=msg), normal=True)
        else:
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
