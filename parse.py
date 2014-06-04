import re
import lxml.html
import urllib
from logging import warning


def contest(id):
    """ Get contest by contest id
        Returns dict. Keys: name, problems
    """
    r = urllib.urlopen("http://codeforces.com/contest/%s" % id)

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
    r = urllib.urlopen("http://codeforces.com/problemset/page/%s" % page)
    assert r.code == 200

    tree = lxml.html.fromstring(r.read())
    rows = tree.xpath("//table[@class='problems']/tr")[1:]

    codes = map(lambda x: x.xpath("./td[1]/a")[0].text.strip(), rows)
    names = map(lambda x: x.xpath("./td[2]/div[1]/a")[0].text.strip(), rows)

    return map(lambda a, b: [a] + [b], codes, names)


def contest_history(page=1):
    " Past contests "
    r = urllib.urlopen("http://codeforces.com/contests/page/%s" % page)
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


if __name__ == "__main__":
    print contest_history(2)
