# coding: utf-8
import re
import glob
import json
import urllib
import datetime
import lxml.html
from logging import warning
from httplib import HTTPException
import html2text as h2t
from lxml import etree


def url_open(url):
    for attempt in range(10):
        try:
            return urllib.urlopen(url)
        except IOError:
            print "Delayed: '%s'" % url
        except HTTPException:
            print "Delayed: '%s'" % url
    raise Exception("Network Error")


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


def contest(id):
    """ Get contest by contest id
        Returns dict. Keys: name, problems
    """
    r = url_open("http://codeforces.com/contest/%s" % id)

    if r.code != 200 or r.url == "http://codeforces.com/":
        warning("Contest '%s' not reachable" % id)
        return

    re_name = "<title>Dashboard - (.+) - Codeforces</title>"
    re_problem = '<option value="(\w+)" >\w+ - (.+)</option>'

    data = r.read()

    return {
        "name": re.search(re_name, data).group(1),
        "problems": re.findall(re_problem, data),
    }


def problemset(page=1):
    """ Entire problemset
        Returns list of tuple. Example tuple: (001-A, Theatre Square)
    """
    r = url_open("http://codeforces.com/problemset/page/%s" % page)
    assert r.code == 200

    tree = lxml.html.fromstring(r.read())
    rows = tree.xpath("//table[@class='problems']/tr")[1:]

    codes = map(lambda x: x.xpath("./td[1]/a")[0].text.strip(), rows)
    names = map(lambda x: x.xpath("./td[2]/div[1]/a")[0].text.strip(), rows)

    return map(lambda a, b: [a] + [b], codes, names)


def problem(code):
    r = url_open("http://codeforces.com/problemset/problem/" +
                 code.strip().replace("-", "/"))

    tree = lxml.html.fromstring(r.read())

    def html(e):
        " inner html "
        return etree.tostring(e).split(">", 1)[1].rsplit("</", 1)[0]

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

    return {
        # meta fields
        "time": tree.xpath("//div[@class='time-limit']/text()")[0],
        "memory": tree.xpath("//div[@class='memory-limit']/text()")[0],
        "input": tree.xpath("//div[@class='input-file']/text()")[0],
        "output": tree.xpath("//div[@class='output-file']/text()")[0],
        "tests": zip(map(lambda e: "\n".join(e.xpath("./text()")), inputs),
                     map(lambda e: "\n".join(e.xpath("./text()")), outputs)),
        # statement fields
        "content": html2text(content),
        "note": html2text(note),
    }


def contest_history(page=1):
    " Past contests "
    r = url_open("http://codeforces.com/contests/page/%s" % page)
    if r.url != "http://codeforces.com/contests/page/%s" % page:
        # Active contest running
        return

    assert r.code == 200
    assert r.url == "http://codeforces.com/contests/page/%s" % page

    tree = lxml.html.fromstring(r.read())
    rows = tree.xpath("//div[@class='contests-table']//table/tr")[1:]

    index = map(lambda x: x.attrib["data-contestid"], rows)
    names = map(lambda x: x.xpath("./td[1]")[0].text.strip(), rows)
    start = map(lambda x: x.xpath("./td[2]")[0].text.strip(), rows)

    return map(lambda a, b, c: [a] + [b] + [c], index, names, start)


# magic
def cf_get_all_users():
    data = url_open("http://codeforces.com/ratings/country/Mongolia").read()
    tree = lxml.html.document_fromstring(data)

    users = []
    for a in tree.xpath("//*[@class='datatable']//table//tr//td[2]/a[2]"):
        users.append(a.text.strip())
    return users


def cf_get_user(handle):
    content = url_open("http://codeforces.com/profile/%s" % handle).read()
    data = content.split("data.push(")[1].split(");")[0]

    log = json.loads(data)[-1]
    now = int(datetime.datetime.now().strftime("%s"))

    return {
        "handle": handle,
        "rating": log[1],
        "change": log[5],
        "active": (now < log[0] / 1000 + 180 * 24 * 3600),
        "contest_at": log[0],
        "contest_id": log[2],
    }


def cf_get_active_users():
    r = []
    for u in cf_get_all_users():
        d = cf_get_user(u)
        if d["active"]:
            r.append(d)

    recent = max(r, key=lambda user: user["contest_at"])
    for i in range(len(r)):
        r[i]["recent"] = (recent["contest_at"] == r[i]["contest_at"])

    return r


def tc_get_all_users():
    data = url_open("http://community.topcoder.com/tc?module=AlgoRank&cc=496").read()
    tree = lxml.html.document_fromstring(data)

    users = []
    for a in tree.xpath("//*[@class='stat']//tr/td[2]/a"):
        id = a.attrib["href"].split("cr=")[1].split("&tab=")[0]
        handle = a.text.strip()

        users.append([handle, id])
    return users


def tc_get_user(handle, id):
    data = url_open("http://community.topcoder.com/tc?module=BasicData&c=dd_rating_history&cr=%s" % id).read()

    row_list = lxml.etree.fromstring(data).xpath("//dd_rating_history/row")

    # find most recent round
    recent = max(row_list, key=lambda row: row.find("date").text)

    return {
        "handle": handle,
        "id": id,
        "rating": int(recent.find("new_rating").text),
        "change": int(recent.find("new_rating").text) - int(recent.find("old_rating").text),
        "active": True,
        "contest_id": int(recent.find("round_id").text),
    }


def tc_get_active_users():
    r = []
    for handle, id in tc_get_all_users():
        d = tc_get_user(handle, id)
        if d["active"]:
            r.append(d)

    recent = max(r, key=lambda user: user["contest_id"])
    for i in range(len(r)):
        r[i]["recent"] = (recent["contest_id"] == r[i]["contest_id"])

    return r


# cli
def problems_translated():
    " Generate file: problems-translated.json "
    def correct(code):
        r = ""
        while code.startswith("0"):
            r += " "
            code = code[1:]

        return r + code

    data = {}

    # code, title, content, note, credits
    for item in glob.glob("Codeforces-mn/Translation/*.md"):
        lines = open(item).read().strip().replace("\r\n", "\n").replace("\r", "\n").split("\n")
        code = correct(re.search("Translation/(\d{3}-\w).md", item).groups()[0])

        # title
        title = lines[0]
        assert lines[1].replace("=", "") == "", repr(lines[1])

        # content
        content = "\n".join(lines[2:-1]).strip()
        if content.startswith("### "):
            content = "\n" + content

        assert content.count("\n### Оролт\n") == 1, "input: " + code + "\n" + content
        assert content.count("\n### Гаралт\n") == 1
        content = content.replace("\n### Оролт\n", "\n## Оролт\n")
        content = content.replace("\n### Гаралт\n", "\n## Гаралт\n")

        # note
        note = ""
        if "# Тэмдэглэл" in content:
            assert content.count("\n### Тэмдэглэл\n") == 1, code
            content, note = content.split("\n### Тэмдэглэл\n", 1)

        # credits
        credits = lines[-1][3:]
        assert lines[-1].startswith("-- "), code + ":" + credits

        data[code] = {
            "title": title,
            "content": content,
            "note": note,
            "credits": credits,
        }

    open("problems-translated.json", "w+").write(json.dumps(data))


if __name__ == "__main__":
    print repr(problem("12-C")["note"])
    print repr(html2text(""))
