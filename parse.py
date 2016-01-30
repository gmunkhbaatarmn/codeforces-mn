# coding: utf-8
import time
import json
import urllib
import datetime
import html2text as h2t
from logging import warning, info
from httplib import HTTPException
from google.appengine.runtime import apiproxy_errors
from lxml import etree


# parse from codeforces.com
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

        print datetime.strptime(c["registrationStartDate"], "%Y-%m-%d %H:%M:%S")
        return

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
