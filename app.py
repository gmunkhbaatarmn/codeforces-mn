import json
from natrix import wsgi_app, db, memcache
import magic as _


class Data(db.Model):
    " Data.write, Data.fetch "
    name = db.StringProperty()
    value = db.TextProperty()

    @classmethod
    def fetch(cls, name, default=None):
        value = memcache.get(name)
        if value:
            return json.loads(value)
        c = cls.all().filter("name =", name).get()
        if c:
            memcache.set(name, c.value)
            return json.loads(c.value)
        return default

    @classmethod
    def write(cls, name, value):
        data = json.dumps(value)
        memcache.set(name, data)

        c = cls.all().filter("name =", name).get() or cls(name=name)
        c.value = data
        c.save()

    @classmethod
    def erase(cls, name):
        memcache.delete(name)
        cls.all().filter("name =", name).delete()


# Handlers

def home(x):
    x.render("home.html")


# --- Problemset ---

def problemset(x, id="1"):
    x.response("OK")


# === Problemset ===

def ratings(x):
    if x.request.path == "/-/ratings":
        Data.write("Rating:codeforces", _.cf_get_active_users())
        Data.write("Rating:topcoder", _.tc_get_active_users())
        x.response("OK")

    x.render("ratings.html")


routes = [
    # Home
    ("/",        home),
    # Contests
    # Problems
    ("/problemset", problemset),
    ("/problemset/page/(\d+)", problemset),
    # ("/problemset/problem/(\d+)/(\w+)(.html)?", problemset_problem),
    ("/-/problemset", problemset),
    # Rating
    ("/ratings", ratings),
    ("/-/ratings", ratings),  # cron
]

config = {
    "context": lambda self: {
        "codeforces": Data.fetch("Rating:codeforces", []),
        "topcoder": Data.fetch("Rating:topcoder", []),
    }
}

app = wsgi_app(routes, config)
