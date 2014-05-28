import re
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


