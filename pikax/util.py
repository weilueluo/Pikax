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
import re
import sys
import time

import requests
import urllib3

from . import settings
from .exceptions import ReqException
from .texts import texts

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

__all__ = ['log', 'req', 'json_loads', 'trim_to_limit', 'clean_filename', 'print_json']


# send request using requests, raise ReqException if fails all retries
def req(url, req_type='get', session=None, params=None, data=None, headers=settings.DEFAULT_HEADERS,
        timeout=settings.TIMEOUT, err_msg=None, log_req=settings.LOG_REQUEST, retries=settings.MAX_RETRIES_FOR_REQUEST,
        proxies=settings.REQUEST_PROXIES, verify=True, requester=None):
    """Send requests according to given parameters using requests library

    **Description**
    This function send request using requests library,
    however its parameters does not accepts all parameters as in requests.get/post
    and some custom parameters is added as shown below

    **Parameters**
    :param requester:
        the function used to make the request call
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
    curr_retries = 1
    req_type = req_type.upper()
    if requester is None:
        handler = requests if session is None else session
        requester = handler.get if 'GET' == req_type else handler.post  # assume post if not 'GET'
    while curr_retries <= retries:
        if log_req:
            log(texts.REQUEST_INFO.format(req_type=req_type, url=url, params=params), end='')
        try:
            # try send request according to parameters
            res = requester(url=url, headers=headers, params=params, timeout=timeout,
                            data=data, proxies=proxies, verify=verify)
            if log_req:
                log(res.status_code)

            # check if request result is normal
            if not res:
                if log_req:
                    log(texts.REQUEST_FALSEY.format(retries=curr_retries), save=True)
            elif res.status_code >= 400:
                if log_req:
                    log(texts.REQUEST_INVALID_STATUS_CODE.format(status_code=res.status_code,
                                                                 retries=curr_retries), save=True)
            else:
                if settings.DELAY_PER_REQUEST is not None:
                    time.sleep(float(settings.DELAY_PER_REQUEST))
                return res

        except requests.exceptions.Timeout as e:
            if log_req:
                log(texts.REQUEST_TIME_OUT.format(retries=curr_retries), save=True)
                log(texts.REQUEST_REASON.format(e=e), save=True, inform=True)
        except requests.exceptions.ConnectionError as e:
            if log_req:
                log(texts.REQUEST_CONNECTION_ERROR.format(retries=curr_retries), save=True)
                log(texts.REQUEST_REASON.format(e=e), save=True, inform=True)
        except requests.exceptions.RequestException as e:
            if log_req:
                log(texts.REQUEST_EXCEPTION.format(retries=curr_retries), save=True, inform=True)
                log(texts.REQUEST_REASON.format(e=e), save=True, inform=True)
                if err_msg:
                    log(texts.REQUEST_MSG.format(msg=err_msg), inform=True)

        curr_retries += 1
        if settings.REQUEST_RETRY_DELAY is not None:
            time.sleep(float(settings.REQUEST_RETRY_DELAY))  # dont retry again too fast

    # if still fails after all retries
    raise ReqException(texts.REQUEST_EXCEPTION_MSG.format(req_type=req_type, url=url, params=params))


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
                log(texts.TRIM_MSG.format(old_len=num_of_items, new_len=limit), inform=True)
            else:
                log(texts.TRIM_NOT_NEEDED.format(len=num_of_items, limit=limit), inform=True)
    return items


# remove invalid file name characters for windows
def clean_filename(string):
    return re.sub(r'[:<>"\\/|?*]', '', str(string))


# used for testing
def print_json(json_obj):
    print(json.dumps(json_obj, indent=4, ensure_ascii=False))


def new_session():
    return requests.Session()


class ProgressPrinter(object):

    def __init__(self):
        self.is_first_print = True
        self.start_time = None
        self.current = None
        self.total = None

    def reset(self):
        self.is_first_print = True
        self.start_time = None
        self.current = None
        self.total = None

    def set_up(self):
        self.start_time = time.time()
        self.current = 0
        self.total = 0
        self.is_first_print = False

    def set_current(self, current):
        self.current = current

    def set_total(self, total):
        self.total = total

    def get_time_left_text(self, curr, total):
        if self.is_first_print:
            self.set_up()
        self.set_current(curr)
        self.set_total(total)
        time_elapsed = time.time() - self.start_time
        seconds = time_elapsed / self.current * (self.total - self.current)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return texts.TIME_FORMAT_HMS.format(h=hours, m=minutes, s=seconds)
        if minutes > 0:
            return texts.TIME_FORMAT_MS.format(m=minutes, s=seconds)
        return texts.TIME_FORMAT_S.format(s=seconds)

    def get_percent(self):
        return self.current / self.total * 100

    def get_progress_text(self, curr, total, msg):
        est_time_left = self.get_time_left_text(curr, total)
        curr_percent = self.get_percent()
        if curr > 1:
            progress_text = texts.PROGRESS_WITH_TIME_LEFT.format(curr=curr, total=total, curr_percent=curr_percent,
                                                                 time_left=est_time_left)
        else:
            progress_text = texts.PROGRESS_TEXT.format(curr=curr, total=total, curr_percent=curr_percent)

        if msg:
            progress_text = f'{msg} | {progress_text}'

        return progress_text

    def print_progress(self, curr, total, msg=None):
        progress_text = self.get_progress_text(curr, total, msg)
        log(progress_text, end='', start=settings.CLEAR_LINE, inform=True)

    def get_done_text(self, msg):
        if msg:
            done_text = texts.DONE_MSG.format(msg=msg)
        else:  # a float, time taken
            done_text = texts.DONE if self.is_first_print \
                else texts.DONE_TIME_TAKEN.format(time_taken=time.time() - self.start_time)

        return done_text

    def print_done(self, msg=None):
        done_text = self.get_done_text(msg)
        log(done_text, normal=True)
        self.reset()


progress_printer = ProgressPrinter()


def print_progress(curr, total, msg=None):
    global progress_printer
    progress_printer.print_progress(curr, total, msg)


def print_done(msg=None):
    global progress_printer
    progress_printer.print_done(msg)


def log(*objects, sep=' ', end='\n', file=sys.stdout, flush=True, start='', inform=False, save=False, error=False,
        warn=False, normal=False):
    """Print according to params and settings.py

    **Description**
    settings.py's LOG_TYPE controls the overall behaviour of this function
    eg. whether each type of log should be available
    caller code controls the type of log
    eg. whether the strings send to log should be type of inform
    This function copied all params of python's print function, except flush is set to True,
    and some custom parameters as shown below

    **Parameters**
    :param flush:
    :param file:
    :param end:
    :param sep:
    :param warn:
        if this is true, a '###' is appended is added at the front of the strings given, default False
    :param normal:
        if this is true, the string given will be printed normally
    :param start:
        the string to print at the start, preceding all other string, including inform & save 's prefix
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

    if settings.LOG_NORMAL and normal:
        print(start, *objects, sep=sep, end=end, file=file, flush=flush)
        return
    if settings.LOG_INFORM and inform:
        print(start, '>>>', *objects, sep=sep, end=end, file=file, flush=flush)
    if settings.LOG_SAVE and save:
        print(start, *objects, sep=sep, end=end, file=open(settings.LOG_FILE, 'a', encoding='utf-8'), flush=False)
    if settings.LOG_INFORM and error:
        print(start, '!!!', *objects, sep=sep, end=end, file=file, flush=flush)
    if settings.LOG_WARN and warn:
        print(start, '###', *objects, sep=sep, end=end, file=file, flush=flush)
    if settings.LOG_STD and not (inform or save or error or warn):
        print(start, *objects, sep=sep, end=end, file=file, flush=flush)
