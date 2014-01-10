import json, webapp2, logging, urllib, magic as _
from google.appengine.api import memcache
from google.appengine.ext import db
from webapp2_extras import jinja2, sessions


class Config(db.Model):#1
    name  = db.StringProperty()
    value = db.TextProperty()

    @classmethod
    def find(cls, **kwargs):
        q = cls.all()
        for k, v in kwargs.items():
            q.filter("%s =" % k, v)

        return q.get()


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
            "codeforces": json.loads(Config.find(name="rating:codeforces").value),
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
    def get(self, contest, problem):
        try:
            source = open("templates/translations/%03d-%s.html" % (int(contest), problem)).read().decode("utf-8")
        except IOError:
            if problem.islower():
                return self.redirect("/problemset/problem/%s/%s" % (contest, problem.upper()))
            return self.abort(404)

        state = ""
        name, content, inputs, outputs, notes, credit = tuple([""] * 6)
        for line in source.split("\n"):
            if line.startswith("<h1"):
                name = line.split('">', 1)[1].replace("</h1>", "")
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
            "codeforces": json.loads(Config.find(name="rating:codeforces").value),
        }

        self.render("error-404.html")
# endfold1


class Codeforces(View):#1
    def get(self):
        data = _.get_active_users()
        memcache.set("rating:codeforces", json.dumps(data))
        c = Config.find(name="rating:codeforces") or Config(name="rating:codeforces")
        c.value = json.dumps(data)
        c.save()
        self.response.write("OK")
# endfold


app = webapp2.WSGIApplication([
    ("/",                               Home),
    ("/contests",                       Contests),
    ("/contest/(\d+)",                  Contest),
    ("/contest/(\d+)/problem/(\w+)",    ContestProblem),
    ("/problemset",                     Problemset),
    ("/problemset/page/(\d+)",          Problemset),
    ("/problemset/problem/(\d+)/(\w+)", ProblemsetProblem),
    ("/ratings",                        Ratings),
    ("/-/codeforces",                   Codeforces),
], debug=True, config={"webapp2_extras.sessions":{"secret_key":"epe9hoongi6Yeeghoo4iopein1Boh9"}})


app.error_handlers[404] = Error(404)
