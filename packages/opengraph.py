import json
from utils import get_url
from logging import warning
from datetime import datetime


APP_TOKEN = "888802607881779|LX-gcFsW9-qGbr2qCXgSJMIO-7Y"


def fetch_id(url):
    " Returns open graph id of URL "
    headers = {"Authorization": "OAuth %s" % APP_TOKEN}
    request_url = "https://graph.facebook.com/v2.5/?id=%s" % url
    response = json.loads(get_url(request_url, headers=headers).content)

    if "og_object" not in response:
        warning("og object is not yet ready:\n%s" % json.dumps(response))
        return 0

    return int(response["og_object"]["id"])


def fetch_comments(ids_codes):
    " Returns list of comments "
    dic = {i: code for i, code in ids_codes}
    headers = {"Authorization": "OAuth %s" % APP_TOKEN}

    fields = "message,created_time,from"
    request = ",".join(map(str, dic.keys()))
    request += "&fields=comments.filter(stream){%s},%s" % (fields, fields)

    request_url = "https://graph.facebook.com/v2.5/comments?ids=%s" % request
    response = json.loads(get_url(request_url, headers=headers).content)

    def reformat_comment(i, comment):
        return {
            "id": int(i),
            "code": dic[int(i)],
            "from_id": int(comment["from"]["id"]),
            "from_name": comment["from"]["name"],
            "created_time": to_timestamp(comment["created_time"]),
            "message": comment["message"],
        }
    # endfold

    result = []
    for i in response:
        for comment in response[i].get("data", []):
            result.append(reformat_comment(i, comment))
            for reply in comment.get("comments", {}).get("data", []):
                result.append(reformat_comment(i, reply))

    return result


# Helper
def to_timestamp(time_string):
    datetime_object = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S+0000")
    return int(datetime_object.strftime("%s"))
