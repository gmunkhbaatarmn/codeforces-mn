from natrix import app, route, data, _


app.config["context"] = lambda x: {
    "codeforces": data.fetch("Rating:codeforces", []),
    "topcoder": data.fetch("Rating:topcoder", []),
}


# --- Todo ---

@route("/problemset")
def problemset(x, id="1"):
    x.response("OK")


@route("/problemset/page/(\d+)")
def problemset_paged(x, id="1"):
    x.response("OK")


# === Done ===

@route("/")
def home(x):
    x.render("home.html")


@route("/ratings")
def ratings(x):
    x.render("ratings.html")


@route("/-/ratings")
def cron_ratings(x):
    data.write("Rating:codeforces", _.cf_get_active_users())
    data.write("Rating:topcoder", _.tc_get_active_users())
    x.response("OK")
