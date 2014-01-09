import lxml.html
import json, datetime
import urllib


def parse_top():
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


def parse_problemset():
    data = open("templates/translations/000-problemset.txt").read().decode("utf-8")

    return json.loads(data)


def get_all_users():
    data = urllib.urlopen("http://codeforces.com/ratings/country/Mongolia").read()
    tree = lxml.html.document_fromstring(data)

    users = []
    for a in tree.xpath("//*[@class='datatable']//table//tr//td[2]/a[2]"):
        users.append(a.text.strip())
    return users


def get_user(handle):
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


def get_active_users():
    r = []
    for u in get_all_users():
        d = get_user(u)
        if d["active"]:
            r.append(d)
    return r

if __name__ == "__main__":
    # print parse_top()
    print get_active_users()
