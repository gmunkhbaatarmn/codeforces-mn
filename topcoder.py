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


def user_info(user_id):
    r = get_url("http://community.topcoder.com/tc?module=BasicData"
                "&c=dd_rating_history&cr=%s" % user_id)

    assert r.status_code == 200  # validate: ok response

    tree = lxml.html.document_fromstring(r.content)
    selector = "//dd_rating_history/row"

    history = tree.xpath(selector)
    if len(history) == 0:
        return {"active": False, "reason": "No history"}

    recent = max(history, key=lambda row: row.find("date").text)
    return {
        "active": True,
        "new_rating": int(recent.find("new_rating").text),
        "old_rating": int(recent.find("old_rating").text),
        "contest_id": int(recent.find("round_id").text),
    }
