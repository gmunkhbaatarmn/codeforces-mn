from natrix import app, route, data, json
from magics import cf_get_active_users, tc_get_active_users
from models import Problem
from logging import warning; warning


def context(self):
    return {
        "int": int,
        "top": data.fetch("Rating:contribution", []),
        "codeforces": data.fetch("Rating:codeforces", []),
        "topcoder": data.fetch("Rating:topcoder", []),
    }


# --- Todo ---

@route("/problemset")
def problemset_index(x, page="1"):
    offset = 100 * (int(page) - 1)

    problems = Problem.all().order("-code").fetch(100, offset=offset)
    count = Problem.all().count(10000)

    x.render("problemset-index.html", locals())


@route("/problemset/page/(\d+)")
def problemset(x, page):
    offset = 100 * (int(page) - 1)

    problems = Problem.all().order("-code").fetch(100, offset=offset)
    count = Problem.all().count(10000)

    x.render("problemset-index.html", locals())


@route("/problemset/update")
def problemset_update(x):
    from parse import problemset
    from logging import warning

    for page in range(1, 21)[::-1]:
        warning("page: %s" % page)

        for attempt in range(10):
            try:
                data = problemset(page)
                break
            except:
                print "Attempt: %s" % attempt
                pass

        for p in data:
            Problem(
                code="%3s-%s" % (p[0][:-1], p[0][-1]),
                title=p[1],
            ).save()


@route("/problemset/migrate")
def migrate(x):
    d = json.loads(open("data.json").read())

    datas = {}

    for p in d:
        translators = p[3].split(", ")

        for t in translators:
            datas[t] = datas.get(t, 0.0) + 1.0 / len(translators)

    contribution = sorted(datas.items(), key=lambda t: -t[1])
    data.write("Rating:contribution", contribution)

    def correct(code):
        r = ""
        while code.startswith("0"):
            r += " "
            code = code[1:]

        return r + code

    for p in d:
        code = correct(p[0])

        pr = Problem.find(code=code) or Problem(code=code)
        pr.title = p[1]
        pr.content = p[4]
        pr.markdown = p[2]
        pr.credits = p[3]
        pr.save()

    x.response("OK")


# === Done ===

@route("/")
def home(x):
    x.render("home.html")


@route("/ratings")
def ratings(x):
    x.render("ratings.html")


@route("/ratings/update")
def ratings_update(x):
    data.write("Rating:codeforces", cf_get_active_users())
    data.write("Rating:topcoder", tc_get_active_users())
    x.response("OK")


app.config["context"] = context
