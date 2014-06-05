from natrix import app, route, data, json
from magics import cf_get_active_users, tc_get_active_users
from models import Problem


def context(self):
    return {
        "codeforces": data.fetch("Rating:codeforces", []),
        "topcoder": data.fetch("Rating:topcoder", []),
    }


# --- Todo ---

@route("/problemset")
def problemset_index(x, id="1"):
    problems = Problem.all().order("-contest_id").\
        order("-problem_id").fetch(100)

    count = Problem.all().count()

    x.render("problemset-index.html", problems=problems,
             count=count)


@route("/problemset/page/(\d+)")
def problemset(x, id="1"):
    problems = Problem.all().order("-contest_id").\
        order("-problem_id").fetch(100)

    count = Problem.all().count()

    x.render("problemset-index.html", problems=problems,
             count=count)


@route("/migrate")
def migrate(x):
    d = json.loads(open("data.json").read())

    for p in d:
        pr = Problem(contest_id=int(p[0]),
                     problem_id=p[1],
                     title=p[2],
                     content=p[5],
                     markdown=p[3],
                     credits=p[4])
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
