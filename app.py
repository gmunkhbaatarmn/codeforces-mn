# coding: utf-8
import json
import time
import topcoder
import codeforces
import opengraph
from datetime import datetime
from markdown2 import markdown
from natrix import app, route, data, info, warning, memcache
from utils import date_format, relative, html2text
from models import Problem, Contest, Suggestion


# Application settings
app.config["session-key"] = "Tiy3ahhiefux2hailaiph4echidaelee3daighahdahruPhoh"
app.config["context"] = lambda x: {
    "date_format": date_format,
    "top": data.fetch("Rating:contribution", []),
    "codeforces": data.fetch("Rating:codeforces", []),
    "topcoder": data.fetch("Rating:topcoder", []),
    "markdown": lambda x: markdown(x, extras=["code-friendly"]),
    "suggestion_count": Suggestion.all(keys_only=True).count(),
    "count_all": data.fetch("count_all"),
    "count_done": data.fetch("count_done"),
    "relative": relative,
    "upcoming_contests": data.fetch("upcoming_contests", []),
    "comments": data.fetch("comments", []),
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
    # Don't redirect: appengine cron job
    if x.request.headers.get("x-appengine-cron"):
        return

    # Don't redirect: appengine taskqueue task
    if x.request.headers.get("x-appengine-taskname"):
        return
    # endfold

    # todo: redirect codeforces-mn.appspot.com  -> codeforces.mn

    # Redirect: `http://www.codeforces.mn/`  -> `https://codeforces.mn/`
    if x.request.url.startswith("http://www."):
        url = "https://%s" % x.request.url[len("http://www."):]
        x.redirect(url, permanent=True)

    # Redirect: `http://codeforces.mn/`      -> `https://codeforces.mn/`
    if x.request.url.startswith("http://"):
        url = "https://%s" % x.request.url[len("http://"):]
        x.redirect(url, permanent=True)

    # Redirect: `https://www.codeforces.mn/` -> `https://codeforces.mn/`
    if x.request.url.startswith("https://www."):
        url = "https://%s" % x.request.url[len("https://www."):]
        x.redirect(url, permanent=True)
    # endfold


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

    x.render("problemset-translate.html", locals(), html2text=html2text)


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

    x.response("Executed seconds: %.1f" % (time.time() - now), log="info")


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

    x.response("Executed seconds: %.1f" % (time.time() - now), log="info")


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
    start_t = time.time()
    complete_update = "complete" in x.request.query

    # Check: new problems
    updated = False
    limit = 50  # check only latest few problems, and it can enough
    for problem in codeforces.api("problemset.problems")["problems"]:
        # Stop: if reach the limit
        limit -= 1
        if not complete_update and limit <= 0:
            break
        # endfold

        code = "%3s-%s" % (problem["contestId"], problem["index"])
        p = Problem.find(code=code) or Problem(code=code)

        # Skip: already added problem
        if p.content:
            continue
        # endfold

        info("Adding problem: %s" % code)
        meta = codeforces.problem(p.code)

        # Skip: if problem parsing failed
        if not meta.get("content"):
            continue

        # Skip: already added problem (by smart duplication detect)
        original = Problem.find(identifier=meta["identifier"])
        if original:
            warning("Can't add problem: %s" % p.code)
            warning("Because it's copy of %s" % original.code)
            continue
        # endfold

        p.title = problem["name"]
        p.content = meta.pop("content")
        p.note = meta.pop("note")
        p.identifier = meta.pop("identifier")
        p.meta_json = json.dumps(meta)
        p.save()

        updated = True

    if updated:
        data.write("count_all", Problem.all(keys_only=True).count(9999))

    # Check: new contests
    updated = False
    limit = 10  # check only latest few contests, and it can enough
    for contest in codeforces.api("contest.list"):
        # Stop: if reach the limit
        limit -= 1
        if not complete_update and limit <= 0:
            break
        # endfold

        # Skip: if not allow submission
        if contest["id"] in [562, 541]:
            continue

        if contest["id"] in [537, 532, 419, 326, 324, 308, 247, 211, 206, 170]:
            continue

        # Skip: if not yet started
        if contest["phase"] == "BEFORE":
            continue
        # endfold

        c = Contest.find(id=contest["id"]) or Contest(id=contest["id"])

        # Skip: if already added
        if c.name:
            continue
        # endfold

        info("Adding contest: %s" % contest["id"])

        # Connect problem index to problemset problem code
        problems = {}
        params = {
            "contestId": contest["id"],
            "from": 1,
            "count": 1,
        }
        for p in codeforces.api("contest.standings", **params)["problems"]:
            code = "%3s-%s" % (p["contestId"], p["index"])
            meta = codeforces.problem(code)

            # skip: if problem parsing failed
            if not meta:
                continue

            # find: original problem from problemset
            original = Problem.find(identifier=meta["identifier"])
            if not original:
                warning("Contest's problem not listed in problemset %s" % code)
                continue

            problems[p["index"]] = original.code
        # endfold

        c.name = contest["name"]
        c.start_at = contest["startTimeSeconds"]
        c.problems_json = json.dumps(problems)
        c.save()

        updated = True

    if updated:
        data.write("count:contest-all", Contest.all(keys_only=True).count(999))
    # endfold

    # Check: upcoming contests
    upcoming_contests = codeforces.upcoming_contests()
    upcoming_contests += topcoder.upcoming_contests()
    upcoming_contests = sorted(upcoming_contests, key=lambda i: i["start_at"])

    data.write("upcoming_contests", upcoming_contests)
    # endfold

    x.response("Executed seconds: %.1f" % (time.time() - start_t), log="info")


@route("/update-comments")
def update_comments(x):
    start_t = time.time()

    # Create opengraph ID for new problems
    for p in Problem.all().filter("og_id =", 0):
        p.og_id = opengraph.fetch_id("https://codeforces.mn" + p.link)
        p.save()

    # Update comments
    comments = []
    problems = [(p.og_id, p.code) for p in Problem.all().order("-code")]
    for page in range((len(problems) + 49) / 50):
        start, until = page * 50, (page + 1) * 50
        comments += opengraph.fetch_comments(problems[start:until])

    comments = sorted(comments, key=lambda i: -i["created_time"])
    data.write("comments", comments[-100:])
    # endfold

    x.response("Executed seconds: %.1f" % (time.time() - start_t), log="info")
