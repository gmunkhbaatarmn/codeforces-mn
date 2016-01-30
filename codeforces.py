import lxml.html
from utils import get_url


def mongolians():
    " Returns list of handle "
    r = get_url("http://codeforces.com/ratings/country/Mongolia")

    assert r.status_code == 200, r.status_code  # validate: ok response
    assert r.final_url is None, r.final_url     # validate: no redirect

    tree = lxml.html.document_fromstring(r.content)
    selector = "//div[contains(@class,'ratingsDatatable')]//table//tr//td[2]//a"

    return [a.text.strip() for a in tree.xpath(selector)]
