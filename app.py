# coding: utf-8
import re
import json
import time
import parse
from datetime import datetime
from hashlib import md5
from markdown2 import markdown
from natrix import app, route, data, info, warning, taskqueue, memcache
from parse import codeforces_ratings, topcoder_ratings, date_format, relative
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
    "relative": relative,
}


# Home
@route(":error-404")
def not_found(x):
    x.render("error-404.html", error="404")


@route(":error-500")
def internal_error(x):
    x.render("error-500.html")


@route("/")
def home(x):
    x.render("home.html")


@route(":before")
def before(x):
    # Redirect www urls to non-www
    if x.request.url.startswith("www."):
        url = "http://%s" % x.request.url.replace("www.", "")
        x.redirect(url, permanent=True)


# Contest
@route("/contests")
def contest_list(x):
    contest_list_paged(x, page=1)


@route("/contests/page/<int>")
def contest_list_paged(x, page):
    offset = 100 * (page - 1)
    contests = Contest.all().order("-id").fetch(100, offset=offset)

    if len(contests) <= 0:
        x.abort(404)

    count = data.fetch("count:contest-all")

    x.render("contest-list.html", locals())


@route("/contest/<int>")
def contest_dashboard(x, id):
    contest = Contest.find_or_404(id=id)

    x.render("contest-dashboard.html", locals())


@route("/contest/<int>/problem/(\w+)")
def contest_problem(x, contest_id, letter):
    letter = letter.upper()

    contest = Contest.find_or_404(id=contest_id)
    code = dict(contest.problems).get(letter)
    if not code:
        x.abort(404)

    problem = Problem.find_or_404(code=code)

    if problem.credits:
        x.render("contest-problem.html", locals())
    else:
        x.render("contest-problem-en.html", locals())


# Problemset
@route("/problemset")
def problemset_index(x):
    problemset_paged(x, page=1)


@route("/problemset/page/<int>")
def problemset_paged(x, page):
    offset = 100 * (page - 1)
    problems = Problem.all().order("-code").fetch(100, offset=offset)

    if len(problems) <= 0:
        x.abort(404)

    x.render("problemset-index.html", locals())


@route("/problemset/problem/<int>/(\w+)")
def problemset_problem(x, contest_id, index):
    index = index.upper()

    problem = Problem.find(code="%3s-%s" % (contest_id, index))

    if not problem:
        # it maybe contest' problem
        contest = Contest.find(id=contest_id)
        if not contest:
            x.abort(404)

        code = dict(contest.problems).get(index)
        if not code:
            x.abort(404)

        x.redirect("/contest/%s" % code.strip().replace("-", "/problem/"))

    if problem.credits:
        x.render("problemset-problem.html", locals())
    else:
        x.render("problemset-problem-en.html", locals())


@route("/problemset/problem/<int>/(\w+)/edit")
def problemset_translate(x, contest_id, index):
    index = index.upper()
    problem = Problem.find_or_404(code="%3s-%s" % (contest_id, index))

    x.render("problemset-translate.html", locals())


@route("/problemset/problem/(\d+)/(\w+)\.html")
def problem_embed(x, contest_id, index):
    # todo: this route is deprecated. remove after extension users upgraded
    extension_problem(x, contest_id, index)


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

    ratings = codeforces_ratings()
    if ratings:
        data.write("Rating:codeforces", ratings)

    ratings = topcoder_ratings()
    if ratings:
        data.write("Rating:topcoder", ratings)

    info("Executed seconds: %.1f" % (time.time() - start))
    x.response("OK")


# Suggestion
@route("/suggestion")
def suggestion_index(x):
    if x.request.query == "logout":
        x.session.pop("moderator", None)

    suggestions = Suggestion.all().order("-added")
    submissions = data.fetch("submissions", [])
    x.render("suggestion-index.html", **locals())


@route("/suggestion#login")
def suggestion_login(x):
    if x.request["password"] in data.fetch("moderators", {}):
        moderators = data.fetch("moderators", {})
        x.session["moderator"] = moderators[x.request["password"]]
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

    problem = Problem.find(code=code)
    if not problem.credits:
        problem.credits = u"[орчуулагдаж байгаа]"
        problem.save()

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

    # - cache count query
    count_all = Problem.all().count(3000)
    count_done = 0
    for p in Problem.all().filter("credits >", ""):
        if p.credits == u"[орчуулагдаж байгаа]":
            continue
        count_done += 1
    data.write("count_all", count_all)
    data.write("count_done", count_done)

    # - update contest translated count
    for c in Contest.all():
        if problem.code not in dict(c.problems).values():
            continue

        count = 0
        for code, p in c.problems_object:
            count += int(p.credits != "")
        c.translated_count = count
        c.save()

    # - update contribution
    contribution = {}
    for p in Problem.all().filter("credits !=", ""):
        translators = p.credits.split(", ")
        for t in translators:
            if t == u"[орчуулагдаж байгаа]":
                continue
            point = (p.meta.get("credit_point") or 1.0) / len(translators)
            contribution[t] = contribution.get(t, 0.0) + point
    contribution = sorted(contribution.items(), key=lambda t: -t[1])
    data.write("Rating:contribution", contribution)

    # - last updated problems (submissions)
    submissions = data.fetch("submissions", [])
    submissions.append({
        "code": suggestion.code,
        "title": title,
        "credits": credits,
        "created_at": int(suggestion.added.strftime("%s")),
        "moderator": x.session["moderator"],
        "published_at": int(datetime.now().strftime("%s")),
    })
    submissions = data.write("submissions", submissions[-150:])

    # - reset cached queries
    memcache.delete("/extension:translated")
    memcache.delete("/extension:contests")

    suggestion.delete()
    x.redirect(str(problem.link), delay=1)


@route("/suggestion#delete")
def suggestion_delete(x):
    if not x.session.get("moderator"):
        x.redirect("/suggestion")

    id = x.request["id"]
    suggestion = Suggestion.get_by_id(int(id))
    code = suggestion.code

    problem = Problem.find(code=code)
    if problem.credits == u"[орчуулагдаж байгаа]":
        if Suggestion.all().filter("code =", code).count() <= 1:
            problem.credits = ""
            problem.save()
    suggestion.delete()

    x.redirect("/suggestion", delay=1.0)


@route("/suggestion/<int>")
def suggestion_review(x, id):
    suggestion = Suggestion.get_or_404(id)
    problem = Problem.find(code=suggestion.code)

    x.render("suggestion-review.html", locals())


# Others
@route("/extension")
def extension(x):
    # - 1. translated problems
    translated = memcache.get("/extension:translated")
    if not translated:
        translated = []
        for p in Problem.all().filter("credits >", ""):
            if p.credits == u"[орчуулагдаж байгаа]":
                continue
            translated.append(p.code)

        translated_set = set(translated)
        for c in Contest.all():
            for letter, code in c.problems:
                if code in translated_set:
                    translated.append("%3s-%s" % (c.id, letter))
        translated = sorted(list(set(translated)))
        memcache.set("/extension:translated", translated)

    x.response.write("|".join([p.strip() for p in translated]))
    x.response.write("\n")

    # - 2. contests "translated/all"
    contests = memcache.get("/extension:contests")
    if not contests:
        contests = [(c.id, c.translated_count, len(c.problems))
                    for c in Contest.all()]
        contests = sorted(contests)
        memcache.set("/extension:contests", contests)

    x.response.write("|".join(["%03d:%s/%s" % t for t in contests]))
    x.response.write("\n")

    # - 3. contribution
    contribution = data.fetch("Rating:contribution")

    x.response.write("|".join(["%s:%s" % (k, v) for k, v in contribution]))
    x.response.write("\n")

    # - 4. all problems count
    x.response.write("%s\n" % data.fetch("count_all"))


@route("/extension/<int>-(\w+)\.html")
def extension_problem(x, contest_id, index):
    index = index.upper()
    problem = Problem.find(code="%3s-%s" % (contest_id, index))
    if not problem:
        # it maybe contest' problem
        contest = Contest.find_or_404(id=int(contest_id))

        code = dict(contest.problems).get(index)
        if not code:
            x.abort(404)

        problem = Problem.find(code=code)

    if not problem or not problem.credits:
        x.abort(404)

    x.render("problem-embed.html", locals())


@route("/update")
def update(x):
    " new contests, new problems "

    # - Check problemset first page
    new_problems = 0
    for code, title in parse.problemset(1):
        if not re.search("^\d+[A-Z]$", code):
            info("SKIPPED: %s" % code)
            continue
        code = "%3s-%s" % (code[:-1], code[-1])
        if code in ["524-A", "524-B"]:
            info("SKIPPED: %s" % code)
            continue

        p = Problem.find(code=code) or Problem(code=code)
        p.title = p.title or title
        if p.content:
            continue

        # new problem found
        new_problems += 1
        meta = parse.problem(p.code)
        if not meta:
            warning("Problem (%s) parsing failed" % p.code)
            continue

        # it's duplicated problem
        identifier = md5(json.dumps(meta["tests"])).hexdigest()
        f = Problem.find(identifier=identifier)
        if f:
            warning("Duplicated problem. %s is copy of %s" % (p.code, f.code))
            continue

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
            if code in ["524-A", "524-B"]:
                info("SKIPPED: %s" % code)
                continue

            meta = parse.problem(code)
            if not meta:
                warning("Can't parse: %s" % code)
                continue

            i = md5(json.dumps(meta["tests"])).hexdigest()
            p = Problem.find(identifier=i)
            if not p:
                warning("Problem not found: %s" % code)
                continue
            problems[letter] = p.code
        c.problems_json = json.dumps(problems)
        c.save()

        # update contest count
        data.write("count:contest-all", Contest.all().count())

    # - Update problems count
    if new_problems > 0:
        data.write("count_all", data.fetch("count_all") + new_problems)
    # endfold

    x.response("OK")


@route("/setup")
def setup(x):
    if "localhost" not in x.request.host:
        x.response("Deny: Only for development")

    start_time = time.time()
    data.write("moderators", {"123": "Admin"})

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

    # count query
    count_all = Problem.all().count(3000)
    count_done = Problem.all().filter("credits >", "").count(3000)
    data.write("count_all", count_all)
    data.write("count_done", count_done)
    # endfold

    info("Executed seconds: %.1f" % (time.time() - start_time))
    x.response("Executed seconds: %.1f" % (time.time() - start_time))


@route("/humans\.txt")
def humans_txt(x):
    x.response(x.render_string("humans.txt"))
