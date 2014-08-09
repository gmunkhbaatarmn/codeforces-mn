import re
import json
import parse
from markdown2 import markdown
from natrix import app, route, data, info, warning
from parse import cf_get_active_users, tc_get_active_users
from models import Problem, Contest, Suggestion


app.config["session-key"] = "Tiy3ahhiefux2hailaiph4echidaelee3daighahdahruPhoh"
app.config["context"] = lambda x: {
    "top": data.fetch("Rating:contribution", []),
    "codeforces": data.fetch("Rating:codeforces", []),
    "topcoder": data.fetch("Rating:topcoder", []),
    "markdown": lambda x: markdown(x, extras=["code-friendly"]),
}


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

    if problem.credits:
        x.render("contest-problem.html", locals())
    else:
        x.render("contest-problem-en.html", locals())


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
    problem = Problem.find(code="%3s-%s" % (contest_id, index))

    if problem.credits:
        x.render("problemset-problem.html", locals())
    else:
        x.render("problemset-problem-en.html", locals())


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


@route("/suggestion")
def suggestion_index(x):
    if x.request.query == "logout":
        x.session.pop("moderator", None)

    suggestions = Suggestion.all().order("-added")
    login_failed = 1
    x.render("suggestion-index.html", **locals())


@route("/suggestion#login")
def suggestion_login(x):
    if x.request["password"] in data.fetch("moderators", {}):
        x.session["moderator"] = 1
        x.redirect("/suggestion")

    suggestions = Suggestion.all().order("-added")
    login_failed = 1
    x.render("suggestion-index.html", **locals())


@route("/suggestion#insert")
def suggestion_insert(x):
    if not x.session.get("moderator"):
        x.redirect("/suggestion")

    code = x.request["code"]
    source = x.request["source"].strip().decode("utf-8")
    source = source.replace("\r\n", "\n")

    title = source.split("\n", 1)[0][2:]
    source = source.split("\n", 1)[1].strip()

    credits = source.rsplit("\n", 1)[1][3:]
    source = source.rsplit("\n", 1)[0].strip()

    note = ""
    # '## Temdeglel'
    heading = u"\n## \u0422\u044d\u043c\u0434\u044d\u0433\u043b\u044d\u043b\n"
    if heading in source:
        note = source.split(heading, 1)[1]
        source = source.split(heading, 1)[0]

    s = Suggestion(code=code)
    s.title = title
    s.content = source
    s.note = note
    s.credits = credits
    s.save()

    # x.flash = ""
    x.redirect("/suggestion")


@route("/suggestion#publish")
def suggestion_publish(x):
    if not x.session.get("moderator"):
        x.redirect("/suggestion")

    id = x.request["id"]
    suggestion = Suggestion.get_by_id(int(id))
    problem = Problem.find(code=suggestion.code)

    source = x.request["source"].strip().decode("utf-8")
    source = source.replace("\r\n", "\n")
    title = source.split("\n", 1)[0][2:]
    source = source.split("\n", 1)[1].strip()
    credits = source.rsplit("\n", 1)[1][3:]
    source = source.rsplit("\n", 1)[0].strip()
    note = ""
    # '## Temdeglel'
    heading = u"\n## \u0422\u044d\u043c\u0434\u044d\u0433\u043b\u044d\u043b\n"
    if heading in source:
        note = source.split(heading, 1)[1]
        source = source.split(heading, 1)[0]

    problem.title = title
    problem.content = source
    problem.note = note
    problem.credits = credits
    problem.save()

    suggestion.delete()

    x.redirect(str(problem.link), delay=1)


@route("/suggestion#delete")
def suggestion_delete(x):
    if not x.session.get("moderator"):
        x.redirect("/suggestion")

    id = x.request["id"]
    suggestion = Suggestion.get_by_id(int(id))
    suggestion.delete()

    x.redirect("/suggestion")


@route("/suggestion/(\d+)")
def suggestion_review(x, id):
    if not x.session.get("moderator"):
        x.redirect("/suggestion")

    suggestion = Suggestion.get_by_id(int(id))
    problem = Problem.find(code=suggestion.code)

    x.render("suggestion-review.html", **locals())


@route("/extension")
def extension(x):
    '''
    self.response.headers["Content-Type"] = "text/plain"

    all_problem = dict(Data.fetch("All:problem"))
    all_similar = Data.fetch("All:similar")
    all_contest = Data.fetch("All:contest")
    contribution = Data.fetch("Rating:contribution")

    for k, v in all_similar.items():
        all_problem[v] = all_problem[k]

    def nozero(x):
        while x.startswith("0"):
            x = x[1:]
        return x

    all_problem = sorted(filter(lambda x: x[1][1], all_problem.items()),
        key=lambda x: x[0])
    self.response.write("|".join([nozero(i[0]) for i in all_problem]) + "\n")
    self.response.write("|".join(["%s:%s/%s" % (i[0], i[1][1], i[1][2]) for i
    in all_contest]) + "\n")
    self.response.write("|".join(["%s:%s" % (k, v) for k, v in contribution]) +
    "\n")
    self.response.write("%s\n" % Data.fetch("Contribution:full"))
    '''


@route("/setup")
def setup(x):
    # data.write("moderators", {"password": "name"})
    # - Ratings
    data.write("Rating:codeforces", cf_get_active_users())
    data.write("Rating:topcoder", tc_get_active_users())
    # - Contests
    for page in range(5, 0, -1):
        info("Contests page: %s" % page)
        for attempt in xrange(10):
            try:
                datas = parse.contest_history(page)
                break
            except:
                warning("Attempt: %s" % attempt)

        for i in datas:
            c = Contest.find(id=int(i[0])) or Contest(id=int(i[0]))
            c.name = i[1]
            c.start = i[2]
            c.save()
    # - Problems
    problems = json.loads(open("problems-meta.json").read())
    translated = json.loads(open("problems-translated.json").read())
    for page in range(20, 0, -1):
        info("Problemset page: %s" % page)
        for attempt in xrange(10):
            try:
                datas = parse.problemset(page)
                break
            except:
                print "Attempt: %s" % attempt

        for code, title in datas:
            if not re.search("^\d+[A-Z]$", code):
                warning("SKIPPED: %s" % code)
                continue
            code = "%3s-%s" % (code[:-1], code[-1])

            p = Problem.find(code=code) or Problem(code=code)
            p.title = title
            if code in problems:
                meta = problems[code]
                p.content = meta.pop("content")
                p.note = meta.pop("note")
                p.meta_json = json.dumps(meta)
            else:
                warning("PROBLEM NOT FOUND: %s" % code)

            # translated fields
            if code in translated:
                p.title = translated[code]["title"]
                p.content = translated[code]["content"]
                p.note = translated[code]["note"] or p.note
                p.credits = translated[code]["credits"]
            p.save()
    # - Contribution point from datastore
    contribution = {}
    for p in Problem.all().filter("credits !=", ""):
        translators = p.credits.split(", ")
        for t in translators:
            point = (p.meta.get("credit_point") or 1.0) / len(translators)
            contribution[t] = contribution.get(t, 0.0) + point
    contribution = sorted(contribution.items(), key=lambda t: -t[1])
    data.write("Rating:contribution", contribution)

    x.response("OK")
