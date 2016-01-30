# coding: utf-8
import time
import json
import urllib
import datetime
import lxml.html
import html2text as h2t
from logging import warning, info
from httplib import HTTPException
from google.appengine.api import urlfetch, urlfetch_errors
from google.appengine.runtime import apiproxy_errors
from lxml import etree


# parse from codeforces.com
def problem(code):
    info("Problem: %s" % code)
    r = url_open("http://codeforces.com/problemset/problem/" +
                 code.strip().replace("-", "/"))
    source = r.read()

    tree = lxml.html.fromstring(source)

    if not tree.xpath("//div[@class='problem-statement']"):
        warning("Unexpected response problem: %s" % code)
        return

    inputs = tree.xpath("//div[@class='input']/pre")
    outputs = tree.xpath("//div[@class='output']/pre")

    content = html(tree.xpath("//div[@class='problem-statement']/div")[1])
    input_text = html(tree.xpath("//div[@class='input-specification']")[0])
    input_text = input_text.replace('<div class="section-title">Input</div>',
                                    "<h2>Оролт</h2>")
    content += input_text

    output_t = html(tree.xpath("//div[@class='output-specification']")[0])
    output_t = output_t.replace('<div class="section-title">Output</div>',
                                "<h2>Гаралт</h2>")
    content += output_t

    note = ""
    if tree.xpath("//div[@class='note']"):
        note = html(tree.xpath("//div[@class='note']")[0])
        note = note.replace('<div class="section-title">Note</div>', "")

    result = {
        # meta fields
        "time": tree.xpath("//div[@class='time-limit']/text()")[0],
        "memory": tree.xpath("//div[@class='memory-limit']/text()|"
                             "//div[@class='memory-limit']/"
                             "span[@class='tex-font-style-bf']/text()")[0],
        "input": tree.xpath("//div[@class='input-file']/text()")[0],
        "output": tree.xpath("//div[@class='output-file']/text()")[0],
        "tests": zip(map(lambda e: sample_test(e), inputs),
                     map(lambda e: sample_test(e), outputs)),
        # statement fields
        "content": html2text(content),
        "note": html2text(note),
    }

    return result


def sample_test(e):
    source = html(e).replace("<br/>", "\n")
    source = source.replace('<span class="tex-span">', "")
    source = source.replace("</span>", "")

    return source


def html(e):
    " inner html "
    return etree.tostring(e).split(">", 1)[1].rsplit("</", 1)[0]


def topcoder_contests():
    data = url_open("http://api.topcoder.com/v2/"
                    "dataScience/challenges/upcoming")

    result = json.loads(data.read())["data"]
    contests = []

    for c in result:
        # Skip if Marathon
        if c["challengeType"] == "Marathon":
            continue

        # Registration starts 4 hour before contest start
        # EST = UTC-05, ESD = UTC-04
        start = c["registrationStartDate"]
        if start[-3:] == "EST":
            df = datetime.timedelta(hours=9)
        elif start[-3:] == "ESD":
            df = datetime.timedelta(hours=8)
        else:
            warning(c["challengeName"] + " unexpected datetime: " + start)
            continue

        # 2016-02-22 17:00 EST -> 2016-02-22 17:00 UTC -> unixtimestamp
        try:
            start = start[:-4]
            start = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M") + df
            start = time.mktime(start.timetuple())
            two_week = 14 * 24 * 60 * 60
            # Skip if not in next 2 week
            if start - time.time() > two_week:
                continue
        except Exception:
            warning(c["challengeName"] + " unexpected behaviour: " + start)
            continue

        contests.append({
            "id": c["challengeId"],
            "name": c["challengeName"],
            "start": int(start),
            "site": "topcoder",
        })

    return contests


# helper functions
def date_format(date, format="%Y/%m/%d"):
    if str(date).isdigit():
        utc_date = datetime.datetime.utcfromtimestamp(int(date))
        utc_date = utc_date + datetime.timedelta(hours=8)
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


def html2text(string):
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


def relative(timestamp):
    if not timestamp:
        return "N/A"

    if isinstance(timestamp, datetime.datetime):
        timestamp = int(timestamp.strftime("%s"))

    seconds = int(datetime.datetime.now().strftime("%s")) - int(timestamp)

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
