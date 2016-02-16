import json
import time
from utils import get_url
from datetime import datetime


APP_TOKEN = "888802607881779|LX-gcFsW9-qGbr2qCXgSJMIO-7Y"


def fetch_id(url, retry=0):
    " Returns open graph id of URL "
    headers = {"Authorization": "OAuth %s" % APP_TOKEN}
    request_url = "https://graph.facebook.com/v2.5/?id=%s" % url
    response = json.loads(get_url(request_url, headers=headers).content)

    # Retry: object is not registered yet
    if not "og_object" in response and retry < 5:
        time.sleep(1.0)
        return fetch_id(url, retry=retry+1)
    # endfold

    return int(response["og_object"]["id"])


def fetch_comments(ids_codes):
    " Returns list of comments "
    dic = {i: code for i, code in ids_codes}
    request = ",".join(map(str, dic.keys()))
    headers = {"Authorization": "OAuth %s" % APP_TOKEN}
    request_url = "https://graph.facebook.com/v2.5/comments?ids=%s" % request
    response = json.loads(get_url(request_url, headers=headers).content)

    # Re-format response
    result = []
    for i in response:
        for c in response[i]["data"]:
            result.append({
                "id": int(i),
                "code": dic[int(i)],
                "from_id": int(c["from"]["id"]),
                "from_name": c["from"]["name"],
                "created_time": to_timestamp(c["created_time"]),
                "message": c["message"],
            })
    # endfold

    return result


# Helper
def to_timestamp(time_string):
    datetime_object = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S+0000")
    return int(datetime_object.strftime("%s"))
