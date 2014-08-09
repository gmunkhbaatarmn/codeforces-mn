from natrix import Model, db, json


class Suggestion(Model):
    code = db.StringProperty()
    title = db.StringProperty()
    content = db.TextProperty(default="")
    note = db.TextProperty(default="")
    credits = db.StringProperty(default="")
    added = db.DateTimeProperty(auto_now=True)


class Problem(Model):
    code = db.StringProperty()
    title = db.StringProperty()

    content = db.TextProperty(default="")
    note = db.TextProperty(default="")
    credits = db.StringProperty(default="")

    # time, memory, input, output, tests
    meta_json = db.TextProperty(default="{}")

    @property
    def link(self):
        return "/problemset/problem/%s" % self.code.replace("-", "/").strip()

    @property
    def link_contest(self):
        return "/contest/%s/problem/%s" % (self.contest_id, self.index)

    @property
    def index(self):
        return self.code.split("-")[1]

    @property
    def contest_id(self):
        return self.code.split("-")[0].strip()

    @property
    def meta(self):
        return json.loads(self.meta_json)


class Contest(Model):
    id = db.IntegerProperty()
    name = db.StringProperty()
    start = db.StringProperty()

    @property
    def problems(self):
        query = Problem.all()
        query = query.filter("code >", "%3s-" % self.id)
        query = query.filter("code <", "%3s-Z" % self.id)

        return query
