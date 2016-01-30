# coding: utf-8
import time
import json
import urllib
import datetime
import lxml.html
import random
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


def topcoder_user(handle, id):
    info("TopCoder: %s" % handle)
    data = url_open("http://community.topcoder.com/tc?module=BasicData"
                    "&c=dd_rating_history&cr=%s" % id).read()

    row_list = lxml.etree.fromstring(data).xpath("//dd_rating_history/row")
    # if empty exclude
    if not row_list:
        return {"active": False}
    # find most recent round
    recent = max(row_list, key=lambda row: row.find("date").text)
    new_rating = int(recent.find("new_rating").text)
    old_rating = int(recent.find("old_rating").text)

    return {
        "handle": handle,
        "id": id,
        "rating": new_rating,
        "change": new_rating - old_rating,
        "active": True,
        "contest_id": int(recent.find("round_id").text),
    }


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


# development only
def mock_problem():
    " Generate random problem information "
    " Returns content, note, credits, meta_json "
    has_credits = random.choice([True, False])
    has_note = random.choice([True, False, False])

    # Lorem paragraphs
    lorem_paragraphs = [
        ("Lorem ipsum dolor sit amet, usu te atqui persequeris neglegentur,"
         " quaeque tacimates an qui. Ad ipsum comprehensam vis, cum deserunt"
         " interpretaris at, case efficiendi no nam. Ut nam nulla blandit. Mei"
         " ad consul labitur tacimates, no vix eros alterum persecuti, in"
         " falli iuvaret lucilius qui. Ut mei copiosae salutandi. Magna ignota"
         " noster no est, nec cu suscipit ocurreret hendrerit."),

        ("Vim ut cetero consetetur, nec purto dolore placerat no, vim menandri"
         " pericula ut. In eius abhorreant pri, velit quodsi in usu. Mei eu"
         " tibique accusam perfecto. Id pro liber maluisset constituam. Eum"
         " etiam apeirian id, vel referrentur complectitur te, fugit tantas"
         " euismod sea ei."),

        ("Ei duo quis zril elaboraret, mea dicant persius dissentiet ad."
         " Ubique adversarium vix ea, mel ad alii nemore scripta. Ne populo"
         " persecuti efficiendi eum, ut vix saperet platonem mnesarchum, sit"
         " ex natum antiopam assentior. Oblique tractatos assentior mei ex,"
         " nam solet eleifend an, mei dicunt vocibus id. Iusto intellegam usu"
         " in, saepe dolorum nostrum cu mei, cu duo constituto efficiendi."
         " Erant pertinax ut has, brute nominati maluisset ei per, alii"
         " persius scribentur et usu."),

        ("Dicat primis viderer sea ut, efficiendi delicatissimi eu per,"
         " docendi verterem cu eos. Ex unum fierent quaestio mei, posidonium"
         " interpretaris cu vix, has officiis recusabo urbanitas in. Atqui"
         " expetenda eum et. Eu utamur eripuit mei, est ei debet detracto"
         " disputando. Mea ferri iriure alterum ad, ei quo vidit iuvaret."),

        ("Vel ei inimicus ocurreret, essent phaedrum ea eam, te integre"
         " imperdiet quaerendum quo. Et nam causae vituperata voluptatibus,"
         " movet dictas iracundia ne his. Vim" " ne purto soluta debitis, cum"
         " vitae pericula evertitur in." " Est at quando nostrud invidunt, sea"
         " essent debitis corpora at. Ei quando tibique nam."),

        ("Ferri dolor molestie in pri, ei vix clita eirmod postulant. Ad qui"
         " nulla noster assueverit. Eu iisque ancillae molestie his, sumo "
         " tantas ne sed, persius mediocrem gubergren vis in. Intellegat "
         " mnesarchum at pri, essent efficiendi id quo."),

        ("Quando ocurreret cu eos. Tollit detraxit cum ut, sea no docendi"
         " platonem, platonem pericula qui cu. Usu ne ferri pericula, et"
         " ullum dicam accusata mea. Nostro commune has in. Ei tale"
         " eloquentiam his, vocibus iracundia nam ad."),

        ("Ea populo nostrud scribentur quo, mei ut cibo dicunt salutandi,"
         " vix ea fierent signiferumque. Novum populo salutandi nec ea, vi"
         " luptatum gloriatur mnesarchum et. Ut pro insolens phaedrum. Cum at"
         " verear praesent, his illud novum consul no."),

        ("Ex oratio audiam facilisis pro, nihil perfecto constituam eam et,"
         " mei id magna habeo. Per ex laudem semper mandamus. An dicta"
         " bonorum tacimates eam, ne saepe nonumy usu. Duis dignissim ius eu."
         " Ius neglegentur signiferumque ei, ne vim verear intellegebat."),

        ("Vis brute nullam mediocritatem ut, corrumpit disputationi ei pri."
         " His no nonumes mentitum temporibus, summo virtute liberavisse pro"
         " ut. Etiam oporteat inimicus ius ex, detracto urbanitas quo no, et"
         " tollit repudiare eum. Ei mei magna habeo labitur. Postulant"
         " molestiae ea vim, adipisci salutatus expetendis cum cu. In movet"
         " denique recusabo duo. Eum atqui labore option at."),
    ]
    # endfold

    content = ""
    for i in range(random.randint(3, 5)):
        content += "\n" + random.choice(lorem_paragraphs) + "\n"
    content = content.strip()

    note = ""
    if has_note:
        note = random.choice(lorem_paragraphs)

    credits = ""
    if has_credits:
        credits = random.choice([
            u"Sugardorj", u"zoloogg", u"gmunkhbaatarmn", u"Энхсанаа",
            u"Sugardorj", u"zoloogg", u"gmunkhbaatarmn", u"Энхсанаа",
            u"Sugardorj", u"zoloogg", u"gmunkhbaatarmn", u"Энхсанаа",
            u"Sugardorj", u"zoloogg", u"gmunkhbaatarmn", u"Энхсанаа",

            u"Төрбат", u"Говьхүү", u"devman", u"khongoro", u"Баттулга",
            u"Төрбат", u"Говьхүү", u"devman", u"khongoro", u"Баттулга",

            u"Адъяа", u"byambadorjp", u"Naranbayar", u"Энхдүүрэн",
            u"Адъяа", u"byambadorjp", u"Naranbayar", u"Энхдүүрэн",

            u"Хүрэлцоож", u"Э.Шүрэнчулуун", u"Баярхүү", u"Gantushig", u"mmur",
            u"Б.Батхуяг", u"Батхишиг", u"footman", u"Дулам", u"Garid",
            u"kami-sama", u"Itgel", u"Мөнхбаяр", u"Хонгор", u"Анхбаяр",
            u"Сүрэнбаяр", u"arigato_dl"])

    meta_json = json.dumps({
        "time": "1 second",
        "memory": "256 megabytes",
        "input": "standard input",
        "output": "standard output",
        "tests": [("1 3 2 1 5 10\n0 10", "30"),
                  ("2 8 4 2 5 10\n20 30\n50 100", "570")],
    })

    return content, note, credits, meta_json
