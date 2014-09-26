# coding: utf-8
import re
import json
import time
import parse
from hashlib import md5
from markdown2 import markdown
from natrix import app, route, data, info, warning, taskqueue
from parse import codeforces_ratings, topcoder_ratings, date_format
from models import Problem, Contest, Suggestion


app.config["session-key"] = "Tiy3ahhiefux2hailaiph4echidaelee3daighahdahruPhoh"
app.config["context"] = lambda x: {
    "date_format": date_format,
    "top": data.fetch("Rating:contribution", []),
    "codeforces": data.fetch("Rating:codeforces", []),
    "topcoder": data.fetch("Rating:topcoder", []),
    "markdown": lambda x: markdown(x, extras=["code-friendly"]),
    "suggestion_count": Suggestion.all().count(),
    "count_all": data.fetch("count_all"),
    "count_done": data.fetch("count_done"),
}


# Home
@route(":error-404")
def not_found(x):
    x.render("error-404.html")


@route(":error-500")
def internal_error(x):
    x.render("error-500.html")


@route("/")
def home(x):
    x.render("home.html")


# Contest
@route("/contests")
def contest_list(x, page="1"):
    contest_list_paged(x, "1")


@route("/contests/page/(\d+)")
def contest_list_paged(x, page):
    offset = 100 * (int(page) - 1)

    contests = Contest.all().order("-id").fetch(100, offset=offset)
    if contests.count() <= 0:
        x.abort(404)

    count = Contest.all().count(1000)

    x.render("contest-list.html", locals())


@route("/contest/(\d+)")
def contest_dashboard(x, id):
    contest = Contest.find(id=int(id))
    if not contest:
        x.abort(404)

    x.render("contest-dashboard.html", locals())


@route("/contest/(\d+)/problem/(\w+)")
def contest_problem(x, contest_id, letter):
    contest = Contest.find(id=int(contest_id))
    if not contest:
        x.abort(404)

    code = dict(contest.problems).get(letter)
    if not code:
        x.abort(404)
    problem = Problem.find(code=code)

    if not problem:
        x.abort(404)

    if problem.credits:
        x.render("contest-problem.html", locals())
    else:
        x.render("contest-problem-en.html", locals())


# Problemset
@route("/problemset")
def problemset_index(x, page="1"):
    problemset_paged(x, "1")


@route("/problemset/page/(\d+)")
def problemset_paged(x, page):
    offset = 100 * (int(page) - 1)
    problems = Problem.all().order("-code").fetch(100, offset=offset)

    if problems.count() <= 0:
        x.abort(404)

    x.render("problemset-index.html", locals())


@route("/problemset/problem/(\d+)/(\w+)")
def problemset_problem(x, contest_id, index):
    problem = Problem.find(code="%3s-%s" % (contest_id, index))

    if not problem:
        x.abort(404)

    if problem.credits:
        x.render("problemset-problem.html", locals())
    else:
        x.render("problemset-problem-en.html", locals())


@route("/problemset/problem/(\d+)/(\w+)\.html")
def problem_embed(x, contest_id, index):
    problem = Problem.find(code="%3s-%s" % (contest_id, index))
    if not problem:
        # it maybe contest' problem
        contest = Contest.find(id=int(contest_id))
        if not contest:
            x.abort(404)
        code = dict(contest.problems).get(index)
        if not code:
            x.abort(404)
        problem = Problem.find(code=code)

    if not problem:
        x.abort(404)

    x.render("problem-embed.html", locals())


@route("/problemset/problem/(\d+)/(\w+)/edit")
def problemset_translate(x, contest_id, index):
    problem = Problem.find(code="%3s-%s" % (contest_id, index))
    if not problem:
        x.abort(problem)

    x.render("problemset-translate.html", locals())


# Rating
@route("/ratings")
def ratings(x):
    x.render("ratings.html")


@route("/ratings/update")
def ratings_update(x):
    taskqueue.add(url="/ratings/update")


@route("/ratings/update#post")
def ratings_update_task(x):
    start = time.time()

    data.write("Rating:codeforces", codeforces_ratings())
    data.write("Rating:topcoder", topcoder_ratings())

    info("Executed seconds: %.1f" % (time.time() - start))
    x.response("OK")


# Suggestion
@route("/suggestion")
def suggestion_index(x):
    if x.request.query == "logout":
        x.session.pop("moderator", None)

    suggestions = Suggestion.all().order("-added")
    x.render("suggestion-index.html", **locals())


@route("/suggestion#login")
def suggestion_login(x):
    if x.request["password"] in data.fetch("moderators", {}):
        x.session["moderator"] = 1
        x.redirect("/suggestion")

    suggestions = Suggestion.all().order("-added")
    login_failed = 1

    x.render("suggestion-index.html", locals())


@route("/suggestion#insert")
def suggestion_insert(x):
    code = x.request["code"]
    source = x.request["source"].strip()
    source = source.replace("\r\n", "\n")

    title = source.split("\n", 1)[0][2:]
    source = source.split("\n", 1)[1].strip()

    credits = source.rsplit("\n", 1)[1][3:]
    source = source.rsplit("\n", 1)[0].strip()

    note = ""
    heading = u"\n## Тэмдэглэл\n"
    if heading in source:
        note = source.split(heading, 1)[1]
        source = source.split(heading, 1)[0]

    s = Suggestion(code=code)
    s.title = title
    s.content = source
    s.note = note
    s.credits = credits
    s.save()

    x.redirect("/suggestion", delay=1)


@route("/suggestion#publish")
def suggestion_publish(x):
    if not x.session.get("moderator"):
        x.redirect("/suggestion")

    id = x.request["id"]
    suggestion = Suggestion.get_by_id(int(id))
    problem = Problem.find(code=suggestion.code)

    source = x.request["source"].strip()
    source = source.replace("\r\n", "\n")
    title = source.split("\n", 1)[0][2:]
    source = source.split("\n", 1)[1].strip()
    credits = source.rsplit("\n", 1)[1][3:]
    source = source.rsplit("\n", 1)[0].strip()
    note = ""

    heading = u"\n## Тэмдэглэл\n"
    if heading in source:
        note = source.split(heading, 1)[1]
        source = source.split(heading, 1)[0]

    problem.title = title
    problem.content = source
    problem.note = note
    problem.credits = credits
    problem.save()

    # cache count query
    count_all = Problem.all().count(3000)
    count_done = Problem.all().filter("credits >", "").count(3000)
    data.write("count_all", count_all)
    data.write("count_done", count_done)

    # update contest translated count
    for c in Contest.all():
        if problem.code not in dict(c.problems).values():
            continue

        count = 0
        for code, problem in c.problems_object:
            count += int(problem.credits != "")
        c.translated_count = count
        c.save()

    # update contribution
    contribution = {}
    for p in Problem.all().filter("credits !=", ""):
        translators = p.credits.split(", ")
        for t in translators:
            point = (p.meta.get("credit_point") or 1.0) / len(translators)
            contribution[t] = contribution.get(t, 0.0) + point
    contribution = sorted(contribution.items(), key=lambda t: -t[1])
    data.write("Rating:contribution", contribution)

    suggestion.delete()
    x.redirect(str(problem.link), delay=1)


@route("/suggestion#delete")
def suggestion_delete(x):
    if not x.session.get("moderator"):
        x.redirect("/suggestion")

    id = x.request["id"]
    suggestion = Suggestion.get_by_id(int(id))
    suggestion.delete()

    x.redirect("/suggestion", delay=1.0)


@route("/suggestion/(\d+)")
def suggestion_review(x, id):
    if not x.session.get("moderator"):
        x.redirect("/suggestion")

    suggestion = Suggestion.get_by_id(int(id))
    if not suggestion:
        x.abort(404)

    problem = Problem.find(code=suggestion.code)

    x.render("suggestion-review.html", locals())


# Others
@route("/extension")
def extension(x):
    # 1. translated problems
    arr = [p.code for p in Problem.all().filter("credits >", "")]
    x.response.write("|".join([p.strip() for p in sorted(arr)]) + "\n")

    # 2. contests "translated/all"
    arr = [(c.id, c.translated_count, len(c.problems)) for c in Contest.all()]
    x.response.write("|".join(["%03d:%s/%s" % t for t in sorted(arr)]) + "\n")

    # 3. contribution
    contribution = data.fetch("Rating:contribution")
    x.response.write("|".join(["%s:%s" % (k, v) for k, v in contribution]))
    x.response.write("\n")

    # 4. all problems count
    x.response.write("%s\n" % Problem.all().count(10000))

    '''
    todo: support for contest problems
    all_problem = dict(Data.fetch("All:problem"))

    for k, v in Data.fetch("All:similar").items():
        all_problem[v] = all_problem[k]

    all_problem = sorted(filter(lambda x: x[1][1], all_problem.items()),
                         key=lambda x: x[0])
    self.response.write("|".join([zerotrim(i[0]) for i in all_problem]) + "\n")
    '''


@route("/update")
def update(x):
    " new contests, new problems "
    # - Check problemset first page
    new_problems = 0
    for code, title in parse.problemset(1):
        if not re.search("^\d+[A-Z]$", code):
            warning("SKIPPED: %s" % code)
            continue
        code = "%3s-%s" % (code[:-1], code[-1])

        p = Problem.find(code=code) or Problem(code=code)
        p.title = p.title or title
        if p.content:
            continue

        # new problem found
        new_problems += 1
        meta = parse.problem(p.code)

        p.content = meta.pop("content")
        p.note = meta.pop("note")
        p.meta_json = json.dumps(meta)
        p.identifier = md5(json.dumps(meta["tests"])).hexdigest()
        p.save()
    # - Check contests first page
    for id, name, start in parse.contest_history(1):
        # read only contest
        if id in [419]:
            continue

        c = Contest.find(id=int(id)) or Contest(id=int(id))
        if c.name:
            continue

        info("new contest found: %s" % id)
        c.name = name
        c.start = start
        problems = {}
        for letter, _ in parse.contest(c.id)["problems"]:
            code = "%3s-%s" % (c.id, letter)
            i = md5(json.dumps(parse.problem(code)["tests"])).hexdigest()
            p = Problem.find(identifier=i)
            if not p:
                warning("Problem not found: %s" % code)
                continue
            problems[letter] = p.code
        c.problems_json = json.dumps(problems)
        c.save()
    # - Update problems count
    if new_problems > 0:
        count_all = data.fetch("count_all")
        data.write("count_all", count_all + new_problems)

    x.response("OK")


@route("/setup")
def setup(x):
    if "localhost" not in x.request.host:
        x.response("Deny: Only for development")

    start_time = time.time()
    # todo: better and easy setup for local development

    # - Ratings
    data.write("Rating:codeforces", codeforces_ratings())
    data.write("Rating:topcoder", topcoder_ratings())
    # - Contests
    for page in range(3, 0, -1):
        info("Contests page: %s" % page)
        for id, name, start in parse.contest_history(page):
            c = Contest.find(id=id) or Contest(id=id)
            c.name = name
            c.start = start
            c.save()
    # - Problemset
    for page in range(3, 0, -1):
        info("Problemset page: %s" % page)
        datas = parse.problemset(page)

        for code, title in datas:
            if not re.search("^\d+[A-Z]$", code):
                warning("SKIPPED: %s" % code)
                continue

            code = "%3s-%s" % (code[:-1], code[-1])

            p = Problem.find(code=code) or Problem(code=code)
            p.title = title
            # fill with fake data
            p.content, p.note, p.credits, p.meta_json = parse.mock_problem()
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

    info("Executed seconds: %.1f" % (time.time() - start_time))
    x.response("Executed seconds: %.1f" % (time.time() - start_time))


@route("/humans\.txt")
def humans_txt(x):
    x.response(x.render_string("humans.txt"))


@route("/robots\.txt")
def robots_txt(x):
    x.response("User-agent: *")
