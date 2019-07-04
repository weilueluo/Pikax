


import sys, json, settings, requests, os


sls = os.linesep
"""
Statistics
"""

def log(*objects, sep=' ', end='\n', file=sys.stdout, flush=True):
    print(*objects, sep=sep, end=end, file=file, flush=flush)


def get_req(url, session=None, params=None, headers=settings.DEFAULT_HEADERS, timeout=settings.TIMEOUT, exception_msg=None, log_req=True, verify=True):
    if log_req:
        log('GET:', str(url), 'with:', str(params))
    retries = 0
    while retries < 3:
        try:
            if session:
                res = session.get(url=url, headers=headers, params=params, timeout=timeout, verify=verify)
            else:
                res = requests.get(url=url, headers=headers, params=params, timeout=timeout, verify=verify)
            if res.status_code >= 400:
                log('Status code error:', res.status_code, retries)
                retries += 1
            else:
                return res
        except requests.exceptions.Timeout as e:
            retries += 1
            log('GET time out:', retries, str(e))
        except requests.exceptions.RequestException as e:
            retries += 1
            if exception_msg:
                log(exception_msg)
            else:
                log('Exception while GET')
            log('Reason:', str(e), 'Retries:', retries)
    log('GET failed:', url)
    return None

def post_req(url, session=None, params=None, data=None, headers=settings.DEFAULT_HEADERS, timeout=settings.TIMEOUT, exception_msg=None, log_req=True):
    if log_req:
        log('POST:', str(url), 'with:', str(params))
    retries = 0
    while retries < 3:
        try:
            if session:
                res = session.post(url=url, headers=headers, data=data, params=params, timeout=timeout)
            else:
                res = requests.post(url=url, headers=headers, data=data, params=params, timeout=timeout)
            if res.status_code >= 400:
                log('Status code error:', res.status_code, retries)
                retries += 1
            else:
                return res
        except requests.exceptions.Timeout as e:
            retries += 1
            log('POST time out:', retries, str(e))
        except requests.exceptions.RequestException as e:
            retries += 1
            if exception_msg:
                log(exception_msg)
            else:
                log('Exception while POST')
            log('Reason:', str(e), 'Retries:', retries)
    log('POST failed:', url)
    return None


def json_loads(text, encoding='utf-8'):
    try:
        return json.loads(text, encoding=encoding)
    except json.JSONDecodeError as e:
        log('Error while turning text to json')
        log('Reason:', str(e))
        return None
