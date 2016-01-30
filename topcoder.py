import json
import lxml.html
from datetime import datetime
from utils import get_url


def upcoming_contests():
    " Returns list of {site, link, start_at} "
    result = []

    r = get_url("http://api.topcoder.com/v2/dataScience/challenges/upcoming")

    assert r.status_code == 200, r.status_code  # validate: ok response
    assert r.final_url is None, r.final_url     # validate: no redirect

    result = []
    for c in json.loads(r.content)["data"]:
        # Skip: marathon (long) contents
        if c["challengeType"] == "Marathon":
            continue
        # endfold

        # Parse: start_at
        start_at = c["registrationStartDate"]
        start_at = datetime.strptime(start_at, "%Y-%m-%d %H:%M EST")
        start_at = int(start_at.strftime("%s"))

        # timezone "EST" is mean "UTC-05"
        start_at += 3600 * 5

        # registration starts 4 hour before contest start
        start_at += 3600 * 4

        # Parse: link
        link = "https://community.topcoder.com/tc?module=MatchDetails&rd=%s"
        link = link % c["challengeId"]
        # endfold

        result.append({
            "site": "topcoder",
            "name": c["challengeName"],
            "link": link,
            "start_at": start_at,
        })

    return result


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
