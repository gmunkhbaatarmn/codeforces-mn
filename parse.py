# coding: utf-8
import re
import lxml.html
import urllib
from logging import warning
from html2text import html2text as h2t
from lxml import etree


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

    result = h2t(string)

    return result


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


def problem(code):
    r = urllib.urlopen("http://codeforces.com/problemset/problem/%s" %
                       code.replace("-", "/"))

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

    output_text = html(tree.xpath("//div[@class='output-specification']")[0])
    output_text = output_text.replace('<div class="section-title">Output</div>',
                                     "<h2>Гаралт</h2>")
    content += output_text

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
    print problem("441-E")["content"]
