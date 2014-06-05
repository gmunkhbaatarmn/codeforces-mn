from natrix import app, route, data, json
from magics import cf_get_active_users, tc_get_active_users
from models import Problem


def context(self):
    return {
        "top": data.fetch("Rating:contribution", []),
        "codeforces": data.fetch("Rating:codeforces", []),
        "topcoder": data.fetch("Rating:topcoder", []),
    }


# --- Todo ---

@route("/problemset")
def problemset_index(x, id="1"):
    problems = Problem.all().order("-code").fetch(100)
    count = Problem.all().count()

    x.render("problemset-index.html", problems=problems,
             count=count)


@route("/problemset/page/(\d+)")
def problemset(x, id="1"):
    problems = Problem.all().order("-code").fetch(100)
    count = Problem.all().count()

    x.render("problemset-index.html", problems=problems,
             count=count)


@route("/migrate")
def migrate(x):
    d = json.loads(open("data.json").read())

    datas = {}

    for p in d:
        translators = p[3].split(", ")

        for t in translators:
            datas[t] = datas.get(t, 0.0) + 1.0 / len(translators)

    data.write("Rating:contribution", sorted(datas.items(), key=lambda t: -t[1]))

    for p in d:
        pr = Problem(code=p[0],
                     title=p[1],
                     content=p[4],
                     markdown=p[2],
                     credits=p[3])
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
