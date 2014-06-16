import re
import json
import parse
from markdown2 import markdown
from natrix import app, route, data, log
from magics import cf_get_active_users, tc_get_active_users
from models import Problem, Contest


def context(self):
    return {
        "int": int,
        "top": data.fetch("Rating:contribution", []),
        "codeforces": data.fetch("Rating:codeforces", []),
        "topcoder": data.fetch("Rating:topcoder", []),
        "markdown": lambda x: markdown(x, extras=["code-friendly"]),
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
    # todo: translated problem count
    offset = 100 * (int(page) - 1)

    contests = Contest.all().order("-id").fetch(100, offset=offset)
    count = Contest.all().count(1000)

    x.render("contest-list.html", locals())


@route("/contests/page/(\d+)")
def contest_list_paged(x, page):
    contest_list(x, page)


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
    # todo: link of non translated problem
    offset = 100 * (int(page) - 1)

    problems = Problem.all().order("-code").fetch(100, offset=offset)
    count = Problem.all().count(10000)

    x.render("problemset-index.html", locals())


@route("/problemset/page/(\d+)")
def problemset_paged(x, page):
    problemset_index(x, page)


@route("/problemset/problem/(\d+)/(\w+)")
def problemset_problem(x, contest_id, index):
    # todo: display extra note
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
    #{ Ratings
    data.write("Rating:codeforces", cf_get_active_users())
    data.write("Rating:topcoder", tc_get_active_users())
    #{ Contests
    for page in range(5, 0, -1):
        log("Contests page: %s" % page)
        for attempt in xrange(10):
            try:
                datas = parse.contest_history(page)
                break
            except:
                log("Attempt: %s" % attempt)

        for i in datas:
            c = Contest.find(id=int(i[0])) or Contest(id=int(i[0]))
            c.name = i[1]
            c.start = i[2]
            c.save()
    #{ Problems
    problems = json.loads(open("problems-meta.json").read())
    for page in range(20, 0, -1):
        log("Problemset page: %s" % page)
        for attempt in xrange(10):
            try:
                datas = parse.problemset(page)
                break
            except:
                print "Attempt: %s" % attempt

        for code, title in datas:
            if not re.search("^\d+[A-Z]$", code):
                log("SKIPPED: %s" % code)
                continue
            code = "%3s-%s" % (code[:-1], code[-1])
            meta = problems[code]

            p = Problem.find(code=code) or Problem(code=code)
            p.title = title
            p.content = meta.pop("content")
            p.note = meta.pop("note")
            p.meta_json = json.dumps(meta)
            p.save()
    x.response("OK")
    #{ (todo:incomplete) Problems translated
    # for code, title, content, note, credits in json.loads(open("data-translated.json").read()):
    #     p = Problem.find(code=code)
    #     p.title = title
    #     p.content = content
    #     p.note = note
    #     p.credits = credits
    #     p.save()
    #{ (todo:easy) Contribution point from datastore
    # for p in Problem.all().filter("credits !=", ""):
    #     translators = p[3].split(", ")
    #     for t in translators:
    #         datas[t] = datas.get(t, 0.0) + 1.0 / len(translators)
    # contribution = sorted(datas.items(), key=lambda t: -t[1])
    # data.write("Rating:contribution", contribution)


app.config["context"] = context
