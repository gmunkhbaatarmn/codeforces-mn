import webapp2
from webapp2_extras import jinja2, sessions


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
    def get(self):
        return self.render("problemset.html")


class ProblemsetProblem(View):#1
    def get(self, contest, problem):
        return self.render("problemset-problem.html")


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
# endfold1


app = webapp2.WSGIApplication([
    ("/",                               Home),
    ("/contests",                       Contests),
    ("/contest/(\d+)",                  Contest),
    ("/contest/(\d+)/problem/(\w+)",    ContestProblem),
    ("/problemset",                     Problemset),
    ("/problemset/problem/(\d+)/(\w+)", ProblemsetProblem),
    ("/ratings",                        Ratings),

], debug=True, config={"webapp2_extras.sessions":{"secret_key":"epe9hoongi6Yeeghoo4iopein1Boh9"}})
