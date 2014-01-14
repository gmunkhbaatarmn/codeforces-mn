import json, webapp2, logging, urllib, magic as _
from google.appengine.api import memcache
from google.appengine.ext import db
from webapp2_extras import jinja2, sessions


class Data(db.Model):#1
    """
        Data.write
        Data.fetch
    """
    name  = db.StringProperty()
    value = db.TextProperty()

    @classmethod
    def fetch(cls, name):
        value = memcache.get(name)
        if value:
            return json.loads(value)
        c = cls.all().filter("name =", name).get()
        if c:
            memcache.set(name, c.value)
            return json.loads(c.value)
        return None

    @classmethod
    def write(cls, name, value):
        data = json.dumps(value)
        memcache.set(name, data)

        c = cls.all().filter("name =", name).get() or cls(name=name)
        c.value = data
        c.save()


class View(webapp2.RequestHandler):#1
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session()

    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)

        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    def context(self):
        return {
            "request":    self.request,
            "session":    self.session,
            "debug":      self.app.debug,
            "flash":      self.flash,
            "url":        webapp2.uri_for,
            "top":        _.parse_top(),
            "codeforces": Data.fetch("rating:codeforces"),
            "topcoder":   Data.fetch("rating:topcoder"),
        }

    def render(self, *args, **kwargs):
        return self.response.write(self.render_string(*args, **kwargs))

    def render_string(self, template, context={}, **kwargs):
        context = dict(self.context().items() + context.items() + kwargs.items())
        return self.jinja2.environment.get_template(template).render(**context)

    @property
    def flash(self):
        return self.session.get_flashes()

    @flash.setter
    def flash(self, item):
        return self.session.add_flash(item)


class Home(View):#1
    def get(self):
        return self.render("home.html")


class Problemset(View):#1
    def get(self, page="1"):
        def nozero(x):
            while x.startswith("0"):
                x = x[1:]
            return x

        return self.render("problemset.html",
                           nozero=nozero,
                           reversed=reversed,
                           page=int(page),
                           data=_.parse_problemset())


class ProblemsetProblem(View):#1
    def get(self, contest, problem, embed):
        try:
            source = _.markdown2html(open("markdown/%03d-%s.md" % (int(contest), problem)).read().decode("utf-8"))
            # source = open("templates/translations/%03d-%s.html" % (int(contest), problem)).read().decode("utf-8")
        except IOError:
            if problem.islower():
                return self.redirect("/problemset/problem/%s/%s" % (contest, problem.upper()))
            return self.abort(404)

        state = ""
        name, content, inputs, outputs, notes, credit = tuple([""] * 6)
        for line in source.split("\n"):
            if line.startswith("<h1"):
                name = line[4:-5]
                state = "content"
                continue
            if line.startswith("<h3") and state == "content":
                state = "inputs"
                continue
            if line.startswith("<h3") and state == "inputs":
                state = "outputs"
                continue
            if line.startswith("<h3") and state == "outputs":
                state = "notes"
                continue
            if line.startswith('<p class="credit"'):
                credit = line
                continue

            if state == "content":
                content += line
                continue
            if state == "inputs":
                inputs += line
                continue
            if state == "outputs":
                outputs += line
                continue
            if state == "notes":
                notes += line
                continue

        if embed == ".html":
            return self.render("problemset-problem-embed.html",
                               contest=contest,
                               problem=problem,
                               name=name,
                               content=content,
                               inputs=inputs,
                               outputs=outputs,
                               notes=notes,
                               credit=credit,
                              )
        return self.render("problemset-problem.html",
                           contest=contest,
                           problem=problem,
                           name=name,
                           content=content,
                           inputs=inputs,
                           outputs=outputs,
                           notes=notes,
                           credit=credit,
                          )


class Contests(View):#1
    def get(self):
        return self.render("contests.html")


class Contest(View):#1
    def get(self, id):
        return self.render("contest.html")


class ContestProblem(View):#1
    def get(self, contest, problem):
        return self.render("contest-problem.html")


class Ratings(View):#1
    def get(self):
        return self.render("ratings.html")


class Error(View, webapp2.BaseHandlerAdapter):#1
    context = lambda x: {}

    def __init__(self, error=None, request=None, response=None):
        self.handler = {404: self.handle_404}[error]
        self.initialize(request, response)

    def __call__(self, request, response, exception):
        self.exception = exception
        self.request   = request
        self.response  = response

        return self.handler()

    def handle_404(self):
        logging.warning("404 Page: %s" % self.request.url)

        # redirect /page/ => /page
        if self.request.path.endswith("/"):
            for r in self.app.router.match_routes:
                if r.regex.match(urllib.unquote(self.request.path[:-1])):
                    return self.redirect(self.request.path[:-1] + "?" + self.request.query_string)
        # redirect /page => /page/
        else:
            for r in self.app.router.match_routes:
                if r.regex.match(urllib.unquote(self.request.path + "/")):
                    return self.redirect(self.request.path + "/?" + self.request.query_string)

        self.context = lambda: {
            "top": _.parse_top(),
            "codeforces": Data.fetch("rating:codeforces"),
            "topcoder":   Data.fetch("rating:topcoder"),
        }

        self.render("error-404.html")
# endfold1


class Hook(View):#1
    """ Called by github's "post-receive-hook"
        Secured by secure key
    """
    secure_key = "ziy1shauphu5LeighaimiSh8goo1ohG7"

    def post(self):
        if self.request.get("key") != self.secure_key:
            logging.warning("Attempt to github-hook")
            return self.abort(404)

        for path in _.changelist(json.loads(self.request.get("payload"))):
            # {Translation/}000-X.md => 000-X
            code = path.replace("Translation/", "").replace(".md", "")
            item = Data.fetch(code=code) or {"code": code}
            item.update(_.parse_markdown(path))
            if not item.get("memory-limit"):
                item.update(_.parse_codeforces(code))

            Data.write("problem:%s" % code, item)


class Codeforces(View):#1
    def get(self):
        Data.write("rating:codeforces", _.cf_get_active_users())
        self.response.write("OK")


class Topcoder(View):#1
    def get(self):
        Data.write("rating:topcoder", _.tc_get_active_users())
        self.response.write("OK")
# endfold


app = webapp2.WSGIApplication([
    ("/",                               Home),
    ("/contests",                       Contests),
    ("/contest/(\d+)",                  Contest),
    ("/contest/(\d+)/problem/(\w+)",    ContestProblem),
    ("/problemset",                     Problemset),
    ("/problemset/page/(\d+)",          Problemset),
    ("/problemset/problem/(\d+)/(\w+)(.html)?", ProblemsetProblem),
    ("/ratings",                        Ratings),
    ("/github-hook",                    Hook),

    ("/-/codeforces",                   Codeforces),
    ("/-/topcoder",                     Topcoder),
], debug=True, config={"webapp2_extras.sessions":{"secret_key":"epe9hoongi6Yeeghoo4iopein1Boh9"}})


app.error_handlers[404] = Error(404)
