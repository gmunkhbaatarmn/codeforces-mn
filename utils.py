# coding: utf-8
import time
import urllib
import html2text as h2t
from datetime import datetime, timedelta
from logging import info
from httplib import HTTPException
from google.appengine.api import urlfetch, urlfetch_errors
from google.appengine.runtime import apiproxy_errors


def get_url(url, params=None, retry=0, headers=None, cookie=None):
    # Build `url` from `params`
    params = params or {}
    if len(params) > 0 and "?" in url:
        url = "%s&%s" % (url, urllib.urlencode(params))
    elif len(params) > 0:
        url = "%s?%s" % (url, urllib.urlencode(params))

    # Build `headers` from `headers`, `cookie`
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X)"
    headers = headers or {}
    headers.update({
        "User-agent": user_agent,
        "Accept-Language": "en-US,en;q=0.8",
    })
    if cookie:
        headers["Cookie"] = cookie
    # endfold

    try:
        return urlfetch.fetch(url=url, headers=headers, deadline=10)
    except (urlfetch_errors.DownloadError,
            urlfetch_errors.DeadlineExceededError,
            urlfetch_errors.InternalTransientError,
            apiproxy_errors.DeadlineExceededError):
        info("URLFetch retried: %r" % url)

    if retry >= 10:
        raise Exception("Network Error: %r" % url)

    time.sleep(1)
    return get_url(url, params=params, retry=retry+1, headers=headers)


def relative(timestamp):
    if not timestamp:
        return "N/A"

    if isinstance(timestamp, datetime):
        timestamp = int(timestamp.strftime("%s"))

    seconds = int(datetime.now().strftime("%s")) - int(timestamp)

    # Just now
    if seconds == 0:
        return u"Дөнгөж сая"

    # Past time
    if 0 < seconds < 60:
        return u"%s секундын өмнө" % seconds
    if 0 < seconds < 60 * 60:
        return u"%s минутын өмнө" % (seconds / 60)
    if 0 < seconds < 60 * 60 * 24:
        return u"%s цагийн өмнө" % (seconds / 60 / 60)

    return u"%s хоногийн өмнө" % (seconds / 60 / 60 / 24)


def date_format(date, format="%Y/%m/%d"):
    if str(date).isdigit():
        utc_date = datetime.utcfromtimestamp(int(date))
        utc_date = utc_date + timedelta(hours=8)
        return utc_date.strftime(format)
    return date


def url_open(url, retry=0):
    # todo: remove `url_open` and replace with `get_url`
    try:
        return urllib.urlopen(url)
    except (apiproxy_errors.DeadlineExceededError, IOError, HTTPException):
        info("Delayed (%s): %s" % (retry, url))

    if retry < 10:
        return url_open(url, retry + 1)

    raise HTTPException("Network Error: %s" % url)


def html2text(string):
    if isinstance(string, str):
        string = string.decode("utf-8")

    string = string.replace("<i>", "")
    string = string.replace("</i>", "")
    string = string.replace('<sup class="upper-index">', "^{")
    string = string.replace('</sup>', "}")

    string = string.replace('<sub class="lower-index">', "_{")
    string = string.replace('</sub>', "}")

    string = string.replace('<span class="tex-span">', "$")
    string = string.replace('</span>', "$")

    h = h2t.HTML2Text()
    h.body_width = 0
    result = h.handle(string).strip()

    result = result.replace(u"## Оролт\n\n", u"## Оролт\n")
    result = result.replace(u"## Гаралт\n\n", u"## Гаралт\n")

    return result
