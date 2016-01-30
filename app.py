# coding: utf-8
import json
import time
import parse
import topcoder
import codeforces
from hashlib import md5
from datetime import datetime
from markdown2 import markdown
from natrix import app, route, data, info, warning, memcache
from parse import date_format, relative, topcoder_contests
from models import Problem, Contest, Suggestion


# Application settings
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
    "upcoming_contests": data.fetch("upcoming_contests", []),
    "topcoder_contests": data.fetch("topcoder_contests", []),
}
app.config["route-shortcut"] = {
    "<code>": "(\w+)",
}
# endfold


# Home
@route(":error-404")
def not_found(x):
    x.render("error-404.html", error="404")


@route(":error-500")
def internal_error(x):
    x.render("error-500.html")


@route(":before")
def before(x):
    # Redirect www urls to non-www
    if x.request.url.startswith("www."):
        url = "http://%s" % x.request.url.replace("www.", "")
        x.redirect(url, permanent=True)


@route("/")
def home(x):
    x.render("home.html")


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


@route("/contest/<int>/problem/<code>")
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


@route("/problemset/problem/<int>/<code>")
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


@route("/problemset/problem/<int>/<code>/edit")
def problemset_translate(x, contest_id, index):
    index = index.upper()
    problem = Problem.find_or_404(code="%3s-%s" % (contest_id, index))

    x.render("problemset-translate.html", locals())


# Rating
@route("/ratings")
def ratings(x):
    x.render("ratings.html")


@route("/ratings/update-codeforces")
def ratings_update_codeforces(x):
    now = time.time()
    period = 180 * 24 * 3600  # 180 days

    result = []
    for handle in codeforces.mongolians():
        ratings = codeforces.api("user.rating", handle=handle)

        # Skip: if not competed
        if not ratings:
            info("Skip: %s. Reason: No rating" % handle)
            continue
        # endfold

        result.append({
            "handle": handle,
            "active": (now - ratings[-1]["ratingUpdateTimeSeconds"]) < period,
            "rating": ratings[-1]["newRating"],
            "change": ratings[-1]["newRating"] - ratings[-1]["oldRating"],
            "contest_id": ratings[-1]["contestId"],
        })

    data.write("Rating:codeforces", result)

    info("Executed seconds: %.1f" % (time.time() - now))
    x.response("Executed seconds: %.1f" % (time.time() - now))


@route("/ratings/update-topcoder")
def ratings_update(x):
    now = time.time()

    result = []
    for handle, id in topcoder.mongolians():
        user = topcoder.user_info(id)

        # Skip: if not competed
        if not user["active"] and user["reason"] == "No history":
            info("Skip: %s. Reason: %s" % (handle, user["reason"]))
            continue
        # endfold

        result.append({
            "id": id,
            "handle": handle,
            "active": user["active"],
            "rating": user["new_rating"],
            "change": user["new_rating"] - user["old_rating"],
            "contest_id": user["contest_id"],
        })

    data.write("Rating:topcoder", result)

    info("Executed seconds: %.1f" % (time.time() - now))
    x.response("Executed seconds: %.1f" % (time.time() - now))


# Suggestion
@route("/suggestion")
def suggestion_index(x):
    if x.request.query == "logout":
        x.session.pop("moderator", None)

    suggestions = Suggestion.all().order("-added")
    submissions = data.fetch("submissions", [])[50:]

    x.render("suggestion-index.html", locals())


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

    # Cache count query
    count_all = Problem.all().count(3000)
    count_done = 0
    for p in Problem.all().filter("credits >", ""):
        if p.credits == u"[орчуулагдаж байгаа]":
            continue
        count_done += 1
    data.write("count_all", count_all)
    data.write("count_done", count_done)

    # Update contest translated count
    for c in Contest.all():
        if problem.code not in dict(c.problems).values():
            continue

        count = 0
        for code, p in c.problems_object:
            count += int(p.credits != "")
        c.translated_count = count
        c.save()

    # Update contribution
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

    # Last updated problems (submissions)
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

    # Reset cached queries
    memcache.delete("/extension:translated")
    memcache.delete("/extension:contests")
    # endfold

    suggestion.delete()
    x.redirect(problem.link, delay=1)


@route("/suggestion#delete")
def suggestion_delete(x):
    if not x.session.get("moderator"):
        x.redirect("/suggestion")

    suggestion = Suggestion.get_by_id(int(x.request["id"]))
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
    # 1. translated problems
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

    # 2. contests "translated/all"
    contests = memcache.get("/extension:contests")
    if not contests:
        contests = [(c.id, c.translated_count, len(c.problems))
                    for c in Contest.all()]
        contests = sorted(contests)
        memcache.set("/extension:contests", contests)

    x.response.write("|".join(["%03d:%s/%s" % t for t in contests]))
    x.response.write("\n")

    # 3. contribution
    contribution = data.fetch("Rating:contribution")

    x.response.write("|".join(["%s:%s" % (k, v) for k, v in contribution]))
    x.response.write("\n")

    # 4. all problems count
    x.response.write("%s\n" % data.fetch("count_all"))


@route("/extension/<int>-<code>.html")
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
    start_time = time.time()
    new_problems = 0

    # Check for new problems
    for problem in codeforces.api("problemset.problems")["problems"]:
        code = "%s-%s" % (str(problem["contestId"]), problem["index"])
        info(code)
        if code in ["524-A", "524-B"]:
            info("SKIPPED: %s" % code)
            continue

        p = Problem.find(code=code) or Problem(code=code)
        if p.content:
            continue

        # new problem found
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

        p.title = problem["name"]
        p.content = meta.pop("content")
        p.note = meta.pop("note")
        p.meta_json = json.dumps(meta)
        p.identifier = md5(json.dumps(meta["tests"])).hexdigest()
        p.save()
        new_problems += 1

    # Check for new contest
    upcoming_contests = []
    for contest in codeforces.api("contest.list"):
        # read only contest
        if contest["id"] in [419]:
            continue

        c = Contest.find(id=int(contest["id"])) or \
            Contest(id=int(contest["id"]))

        if c.problems:
            continue

        info("new contest found: %s" % contest["id"])
        c.name = contest["name"]
        c.start = str(contest["startTimeSeconds"])

        if contest["startTimeSeconds"] >= start_time:
            info("Contest %s: Not started" % (str(contest["id"])))
            upcoming_contests.append({
                "id": contest["id"],
                "name": contest["name"],
                "start": contest["startTimeSeconds"],
                "site": "codeforces",
            })
            c.save()
            continue

        problems = {}
        params = {
            "from": 1,
            "count": 1,
            "contestId": contest["id"],
        }
        for problem in codeforces.api("contest.standings", **params)["problems"]:
            code = "%3s-%s" % (problem["contestId"], problem["index"])
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
            problems[problem["index"]] = p.code
        c.problems_json = json.dumps(problems)
        c.save()

    # update contest count
    data.write("count:contest-all", Contest.all().count())

    # Update problems count
    if new_problems > 0:
        data.write("count_all", data.fetch("count_all", 0) + new_problems)
    # endfold
    # Update upcoming contest
    data.write("upcoming_contests", upcoming_contests)
    data.write("topcoder_contests", topcoder_contests())
    # endfold

    info("OK")
    x.response("OK")
