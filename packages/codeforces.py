# coding: utf-8
import json
import urllib
import lxml.html
import lxml.etree
from hashlib import md5
from logging import warning
from utils import get_url


def api(path, **kwargs):
    url = "http://codeforces.com/api/" + path

    if kwargs:
        url += "?" + urllib.urlencode(kwargs.items())

    response = json.loads(get_url(url).content)

    assert response["status"] == "OK", response
    return response["result"]


def upcoming_contests():
    " Returns list of {site, link, start_at} "
    result = []

    for contest in api("contest.list"):
        # Skip: already started contest
        if contest["phase"] != "BEFORE":
            continue
        # endfold

        result.append({
            "site": "codeforces",
            "name": contest["name"],
            "link": "http://codeforces.com/contests/%s" % contest["id"],
            "start_at": contest["startTimeSeconds"],
        })

    return result


def mongolians():
    " Returns list of handle "
    r = get_url("http://codeforces.com/ratings/country/Mongolia")

    assert r.status_code == 200, r.status_code  # validate: ok response
    assert r.final_url is None, r.final_url     # validate: no redirect

    tree = lxml.html.document_fromstring(r.content)
    selector = "//div[contains(@class,'ratingsDatatable')]//tr//td[2]//a"

    return [i.text.strip() for i in tree.xpath(selector)]


def problem(code):
    # Fetch html source
    url = "http://codeforces.com/problemset/problem/%s/%s"
    r = get_url(url % tuple(code.strip().split("-")))

    try:
        assert r.status_code == 200, r.status_code  # validate: ok response
        assert r.final_url is None, r.final_url     # validate: no redirect
    except AssertionError:
        warning("Can't parse problem: %s" % code, exc_info=True)
        return {}
    # endfold

    tree = lxml.html.fromstring(r.content)

    # Validate: must be problem statement available
    if not tree.xpath("//div[@class='problem-statement']"):
        warning("Can't parse problem: %s" % code, exc_info=True)
        return {}
    # endfold

    # Parse: time limit
    time_limit = tree.xpath("//div[@class='time-limit']/text()")[0]
    time_limit = time_limit.replace("seconds", "")
    time_limit = time_limit.replace("second", "").strip()

    # Parse: memory limit
    memory_limit = tree.xpath("string(//div[@class='memory-limit'])")
    memory_limit = memory_limit.replace("memory limit per test", "")
    memory_limit = int(memory_limit.replace("megabytes", "").strip())

    # Parse: input file
    input_file = tree.xpath("//div[@class='input-file']/text()")[0]
    input_file = input_file.replace("standard input", "").strip()

    # Parse: output file
    output_file = tree.xpath("//div[@class='output-file']/text()")[0]
    output_file = output_file.replace("standard output", "").strip()

    # Parse: tests
    test_inputs = tree.xpath("//div[@class='input']/pre")
    test_inputs = map(lambda e: to_html(e), test_inputs)
    test_inputs = map(lambda t: t.replace("<br/>", "\n"), test_inputs)

    test_outputs = tree.xpath("//div[@class='output']/pre")
    test_outputs = map(lambda e: to_html(e), test_outputs)
    test_outputs = map(lambda t: t.replace("<br/>", "\n"), test_outputs)

    tests = zip(test_inputs, test_outputs)
    # endfold

    # Parse: content
    input_t = to_html(tree.xpath("//div[@class='input-specification']"))
    input_t = input_t.replace('<div class="section-title">Input</div>',
                              "<h2>Оролт</h2>")

    output_t = to_html(tree.xpath("//div[@class='output-specification']"))
    output_t = output_t.replace('<div class="section-title">Output</div>',
                                "<h2>Гаралт</h2>")

    content = to_html(tree.xpath("//div[@class='problem-statement']/div")[1])
    content += input_t
    content += output_t
    content = ensure_unicode(content)

    # Parse: note
    if tree.xpath("//div[@class='note']"):
        note = to_html(tree.xpath("//div[@class='note']"))
        note = note.replace('<div class="section-title">Note</div>', "")
    else:
        note = ""

    # Parse: identifier (must be unique for each problem)
    identifier = md5(json.dumps(tests)).hexdigest()
    # endfold

    return {
        # meta fields
        "time_limit": time_limit,      # seconds
        "memory_limit": memory_limit,  # megabytes
        "input_file": input_file,
        "output_file": output_file,
        "tests": tests,

        # non-meta fields
        "content": content,
        "note": note,
        "identifier": identifier,
    }


# Helper functions
def to_html(element):
    " Returns html source of element "

    # get first element of list
    if isinstance(element, list):
        element = element[0]

    # convert element to html source
    html_source = lxml.etree.tostring(element)

    # unwrap parent tag
    html_source = html_source.split(">", 1)[1].rsplit("</", 1)[0]

    return html_source


def ensure_unicode(string):
    if isinstance(string, str):
        string = string.decode("utf-8")
    return string
