from natrix import app, route, data, json
from magics import cf_get_active_users, tc_get_active_users
from models import Problem, Contest
from logging import warning;warning


def context(self):
    return {
        "int": int,
        "top": data.fetch("Rating:contribution", []),
        "codeforces": data.fetch("Rating:codeforces", []),
        "topcoder": data.fetch("Rating:topcoder", []),
    }


# --- Todo ---

@route("/problemset/data")
def problemset_data(x):
    problems = Problem.all().order("-code")

    x.response([p.code for p in problems], encode="json")

# === Done ===

@route("/")
def home(x):
    x.render("home.html")


@route("/contests")
def contest_list(x, page="1"):
    offset = 100 * (int(page) - 1)

    contests = Contest.all().order("-id").fetch(100, offset=offset)
    count = Contest.all().count(1000)

    x.render("contest-list.html", locals())


@route("/contests/page/(\d+)")
def contest_list_paged(x, page):
    offset = 100 * (int(page) - 1)

    contests = Contest.all().order("-id").fetch(100, offset=offset)
    count = Contest.all().count(1000)

    x.render("contest-list.html", locals())


@route("/contest/(\d+)")
def contest_dashboard(x, id):
    contest = Contest.find(id=int(id))
    x.render("contest-dashboard.html", locals())


@route("/contest/(\d+)/problem/(\w+)")
def contest_problem(x, contest_id, index):
    problem = Problem.find(code="%3s-%s" % (contest_id, index))

    x.render("contest-problem.html", locals())


@route("/problemset")
def problemset_index(x, page="1"):
    offset = 100 * (int(page) - 1)

    problems = Problem.all().order("-code").fetch(100, offset=offset)
    count = Problem.all().count(10000)

    x.render("problemset-index.html", locals())


@route("/problemset/page/(\d+)")
def problemset_paged(x, page):
    offset = 100 * (int(page) - 1)

    problems = Problem.all().order("-code").fetch(100, offset=offset)
    count = Problem.all().count(10000)

    x.render("problemset-index.html", locals())


@route("/problemset/problem/(\d+)/(\w+)")
def problemset_problem(x, contest_id, index):
    problem = Problem.find(code="%3s-%s" % (contest_id, index))

    x.render("problemset-problem.html", locals())


@route("/problemset/problem/(\d+)/(\w+)/edit")
def problemset_translate(x, contest_id, index):
    problem = Problem.find(code="%3s-%s" % (contest_id, index))

    x.render("problemset-translate.html", locals())


@route("/ratings")
def ratings(x):
    x.render("ratings.html")


@route("/ratings/update")
def ratings_update(x):
    data.write("Rating:codeforces", cf_get_active_users())
    data.write("Rating:topcoder", tc_get_active_users())
    x.response("OK")


@route("/setup")
def setup(x):
    # Contests
    from parse import contest_history
    from logging import warning

    for page in range(1, 6)[::-1]:
        warning("Contests page: %s" % page)

        for attempt in range(10):
            try:
                datas = contest_history(page)
                break
            except:
                warning("Attempt: %s" % attempt)
                pass

        for i in datas:
            c = Contest()
            c.id = int(i[0])
            c.name = i[1]
            c.start = i[2]
            c.save()

    # Problems
    from parse import problemset

    for page in range(1, 21)[::-1]:
        warning("Problemset page: %s" % page)

        for attempt in range(10):
            try:
                datas = problemset(page)
                break
            except:
                print "Attempt: %s" % attempt
                pass

        for p in datas:
            pr = Problem()
            pr.code = "%3s-%s" % (p[0][:-1], p[0][-1])
            pr.title = p[1]
            pr.save()

    # Problems migrate
    d = json.loads(open("data-problems.json").read())

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
        pr.markdown = p[2]
        pr.credits = p[3]
        pr.save()

    # Ratings
    data.write("Rating:codeforces", cf_get_active_users())
    data.write("Rating:topcoder", tc_get_active_users())

    # x.redirect("/")
    x.response("OK")


@route("/migrate")
def migrate(x):
    r = []
    for code, meta in sorted(json.loads(open("problems-meta.json").read()).items()):
        p = Problem.find(code=code)
        p.meta_json = json.dumps(meta)
        p.save()

    x.response("\n".join(r))


app.config["context"] = context
