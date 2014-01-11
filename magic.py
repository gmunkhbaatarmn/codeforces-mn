import lxml.html, lxml.etree
import json, datetime
import urllib


def parse_top():#1
    data = open("templates/translations/000-data.txt").read().decode("utf-8")

    top = {
        "total": int(data.split("\r")[3]),
        "done":  0,
        "users": [],
    }

    for t in data.split("\r")[2].split("|"):
        top["users"].append({
            "point": t.split(":")[1],
            "name": t.split(":")[0],
        })
        top["done"] += float(t.split(":")[1])

    return top


def parse_problemset():#1
    data = open("templates/translations/000-problemset.txt").read().decode("utf-8")

    return json.loads(data)


def cf_get_all_users():#1
    data = urllib.urlopen("http://codeforces.com/ratings/country/Mongolia").read()
    tree = lxml.html.document_fromstring(data)

    users = []
    for a in tree.xpath("//*[@class='datatable']//table//tr//td[2]/a[2]"):
        users.append(a.text.strip())
    return users


def cf_get_user(handle):#1
    content = urllib.urlopen("http://codeforces.com/profile/%s" % handle).read()
    data = content.split("data.push(")[1].split(");")[0]

    log = json.loads(data)[-1]
    now = int(datetime.datetime.now().strftime("%s"))

    return {
        "handle": handle,
        "rating": log[1],
        "change": log[5],
        "active": (now < log[0] / 1000 + 180 * 24 * 3600),
        "last_contest_at": log[0],
        "last_contest_id": log[2],
    }


def cf_get_active_users():#1
    r = []
    for u in cf_get_all_users():
        d = cf_get_user(u)
        if d["active"]:
            r.append(d)
    return r
# endfold


def tc_get_all_users():#1
    # data = urllib.urlopen("http://community.topcoder.com/tc?module=AlgoRank&cc=496").read()
    data = open("topcoder-mn.html").read()
    tree = lxml.html.document_fromstring(data)

    users = []
    for a in tree.xpath("//*[@class='stat']//tr/td[2]/a"):
        id = a.attrib["href"].split("cr=")[1].split("&tab=")[0]
        handle = a.text.strip()

        users.append([handle, id])
    return users


def tc_get_user(handle, id):#1
    print handle
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
    return r
# endfold


if __name__ == "__main__":
    # print parse_top()
    # print tc_get_all_users()
    print tc_get_active_users()
