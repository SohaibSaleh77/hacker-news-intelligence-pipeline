import logging
import time
import sys
import re
from functools import wraps

def get_log(name):
    log = logging.getLogger(name)
    if not log.handlers:
        log.setLevel(logging.INFO)
        fmt = logging.Formatter('%(asctime)s | %(levelname)-8s | %(funcName)-20s | %(message)s')
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(fmt)
        log.addHandler(ch)
    return log

def timer(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        diff = time.time() - start
        log = get_log("Utils")
        log.info(f"'{func.__name__}' took {diff:.2f}s.")
        return res
    return wrap

def retry(retries=3, delay=2):
    def dec(func):
        @wraps(func)
        def wrap(*args, **kwargs):
            log = get_log("Utils")
            r = 0
            while r < retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    r += 1
                    log.warning(f"Error in {func.__name__}: {e}. Retry {r}/{retries} in {delay}s...")
                    time.sleep(delay)
            log.error(f"{func.__name__} failed after {retries} tries.")
            return None
        return wrap
    return dec

def clean(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = text.replace('\n', ' ').replace('\r', ' ')
    return re.sub(r'\s+', ' ', text).strip()

def get_domain(url):
    if not isinstance(url, str):
        return "Unknown"
    match = re.search(r'https?://(?:www\.)?([^/]+)', url)
    return match.group(1) if match else "Unknown"
