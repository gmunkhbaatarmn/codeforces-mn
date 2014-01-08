import json


def parse_top():
    data = open("templates/translations/000-data.txt").read().decode("utf-8")

    top = {
        "total": int(data.split("\r")[3]),
        "done":  0,
        "users": [],
    }

    for t in data.split("\r")[2].split("|"):
        top["users"].append({
            "point": t.split(":")[1],
            "name": t.split(":")[0],
        })
        top["done"] += float(t.split(":")[1])

    return top


def parse_problemset():
    data = open("templates/translations/000-problemset.txt").read().decode("utf-8")

    return json.loads(data)


if __name__ == "__main__":
    print parse_top()
