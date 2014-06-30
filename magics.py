# coding: utf-8
import lxml.html, lxml.etree
import json, datetime
import urllib, re
import markdown2
import logging
from utils import url_open


def changelist(payload):#1
    changes = set([])

    for commit in payload["commits"]:
        for path in commit["added"] + commit["modified"] + commit["removed"]:
            if re.search("^Translation/\d{3}-[A-Z].md$", path):
                changes.add(path[12:-3])

    return list(changes)


def parse_markdown(code):#1
    logging.info("Github parse: https://raw.github.com/gmunkhbaatarmn/codeforces-mn/master/Translation/%s.md" % code)
    data = url_open("https://raw.github.com/gmunkhbaatarmn/codeforces-mn/master/Translation/%s.md" % code).read().decode("utf-8")
    html = markdown2.markdown(data, extras=["code-friendly"])
    html = html.replace("\n\n<p", "\n<p")
    html = html.replace("\n\n<h3", "\n<h3")

    item = {
        "name": "UN-NAMED",
        "content": "",
        "inputs": "",
        "outputs": "",
        "credit": "UN-CREDITED",
        "notes": "",
    }

    state = ""
    for line in html.split("\n"):
        if line.startswith("<h1"):
            item["name"] = line[4:-5]
            state = "content"
            continue
        if line.startswith("<h3") and state == "content":
            state = "inputs"
            continue
        if line.startswith("<h3") and state == "inputs":
            state = "outputs"
            continue
        if line.startswith("<h3") and state == "outputs":
            state = "notes"
            continue
        if line.startswith('<p>-- '):
            item["credit"] = line[6:-4]
            continue

        if state == "content":
            item["content"] += "\n" + line
            continue
        if state == "inputs":
            item["inputs"]  += "\n" + line
            continue
        if state == "outputs":
            item["outputs"] += "\n" + line
            continue
        if state == "notes":
            item["notes"]   += "\n" + line
            continue
    return item


def parse_codeforces(code):#1
    logging.info("Codeforces parse: http://codeforces.com/problemset/problem/%s/%s" % (int(code.split("-")[0]), code.split("-")[1]))
    r = url_open("http://codeforces.com/problemset/problem/%s/%s" % (int(code.split("-")[0]), code.split("-")[1]))

    if r.url == "http://codeforces.com/":
        logging.info("Codeforces parse: http://codeforces.com/problemset/problem/%s/%s1" % (int(code.split("-")[0]), code.split("-")[1]))
        r = url_open("http://codeforces.com/problemset/problem/%s/%s1" % (int(code.split("-")[0]), code.split("-")[1]))
    data = r.read().decode("utf-8")

    item = {
        "samples": [],
        "memory-limit": data.split('property-title">memory limit per test</div>', 1)[1].split("</div>", 1)[0],
        "time-limit": data.split('property-title">time limit per test</div>', 1)[1].split("</div", 1)[0],
        "input-file": data.split('property-title">input</div>', 1)[1].split("</div>", 1)[0],
        "output-file": data.split('property-title">output</div>', 1)[1].split("</div>", 1)[0],
    }

    if '<div class="sample-test"><div class="input">' in data:
        for line in data.split('<div class="sample-test"><div class="input">', 1)[1].split("</div>\n")[0].split('<div class="input">'):
            line = line.replace('<div class="title">Input</div><pre>', "")
            line = line.replace("<br />", "\n")

            inp, out = line.split('</pre></div><div class="output"><div class="title">Output</div><pre>')
            inp = inp.strip()
            out = out.split("</pre></div>", 1)[0].strip()

            item["samples"].append([inp, out])

    item["memory-limit"] = item["memory-limit"].replace("megabytes", u"мегабайт")
    item["time-limit"]   = item["time-limit"].replace("seconds", u"секунд").replace("second", u"секунд")
    return item
# endfold


def cf_get_all_users():#1
    data = url_open("http://codeforces.com/ratings/country/Mongolia").read()
    tree = lxml.html.document_fromstring(data)

    users = []
    for a in tree.xpath("//*[@class='datatable']//table//tr//td[2]/a[2]"):
        users.append(a.text.strip())
    return users


def cf_get_user(handle):#1
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


def cf_get_active_users():#1
    r = []
    for u in cf_get_all_users():
        d = cf_get_user(u)
        if d["active"]:
            r.append(d)

    recent = max(r, key=lambda user: user["contest_at"])
    for i in range(len(r)):
        r[i]["recent"] = (recent["contest_at"] == r[i]["contest_at"])

    return r
# endfold


def tc_get_all_users():#1
    data = urllib.urlopen("http://community.topcoder.com/tc?module=AlgoRank&cc=496").read()
    tree = lxml.html.document_fromstring(data)

    users = []
    for a in tree.xpath("//*[@class='stat']//tr/td[2]/a"):
        id = a.attrib["href"].split("cr=")[1].split("&tab=")[0]
        handle = a.text.strip()

        users.append([handle, id])
    return users


def tc_get_user(handle, id):#1
    data = urllib.urlopen("http://community.topcoder.com/tc?module=BasicData&c=dd_rating_history&cr=%s" % id).read()

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


def tc_get_active_users():#1
    r = []
    for handle, id in tc_get_all_users():
        d = tc_get_user(handle, id)
        if d["active"]:
            r.append(d)

    recent = max(r, key=lambda user: user["contest_id"])
    for i in range(len(r)):
        r[i]["recent"] = (recent["contest_id"] == r[i]["contest_id"])

    return r
# endfold


if __name__ == "__main__":
    pass
