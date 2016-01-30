import json
import urllib
import lxml.html
from utils import get_url


def api(path, **kwargs):
    url = "http://codeforces.com/api/" + path

    if kwargs:
        url += "?" + urllib.urlencode(kwargs.items())

    response = json.loads(get_url(url).content)

    assert response["status"] == "OK", response
    return response["result"]


def mongolians():
    " Returns list of handle "
    r = get_url("http://codeforces.com/ratings/country/Mongolia")

    assert r.status_code == 200, r.status_code  # validate: ok response
    assert r.final_url is None, r.final_url     # validate: no redirect

    tree = lxml.html.document_fromstring(r.content)
    selector = "//div[contains(@class,'ratingsDatatable')]//table//tr//td[2]//a"

    return [i.text.strip() for i in tree.xpath(selector)]
