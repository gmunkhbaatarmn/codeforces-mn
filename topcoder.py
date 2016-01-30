import lxml.html
from utils import get_url


def mongolians():
    " Returns list of (handle, id) "
    r = get_url("http://community.topcoder.com/tc?module=AlgoRank&cc=496")

    assert r.status_code == 200  # validate: ok response

    tree = lxml.html.document_fromstring(r.content)
    selector = "//*[@class='stat']//tr/td[2]/a"

    result = []
    for a in tree.xpath(selector):
        id = int(a.attrib["href"].split("cr=")[1].split("&tab=")[0])
        handle = a.text.strip()
        result.append([handle, id])

    return result
