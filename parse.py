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

    data = r.read()

    tree = lxml.html.fromstring(data)

    codes = map(lambda x: x.text.strip(),
                tree.xpath("//table[@class='problems']/tr/td[1]/a"))
    names = map(lambda x: x.text.strip(),
                tree.xpath("//table[@class='problems']/tr/td[2]/div[1]/a"))

    problems = map(lambda a, b: [a] + [b], codes, names)

    return problems


if __name__ == "__main__":
    print problemset(30)[-1]
