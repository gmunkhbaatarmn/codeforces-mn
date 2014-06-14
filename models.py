from natrix import db, json


class Problem(db.Model):
    code = db.StringProperty()
    title = db.StringProperty()

    statement = db.TextProperty(default="")
    note = db.TextProperty(default="")
    credits = db.StringProperty(default="")

    # in_problemset = db.BooleanProperty()
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

    @classmethod
    def find(cls, **kwargs):
        q = cls.all()
        for k, v in kwargs.items():
            q.filter("%s =" % k, v)

        return q.get()

    @property
    def meta(self):
        return json.loads(self.meta_json)


class Contest(db.Model):
    id = db.IntegerProperty()
    name = db.StringProperty()
    start = db.StringProperty()
    # duration = db.IntegerProperty()

    translated_count = db.IntegerProperty(default=0)

    @property
    def problems_count(self):
        return self.problems.count()

    @property
    def problems(self):
        query = Problem.all()
        query = query.filter("code >", "%3s-" % self.id)
        query = query.filter("code <", "%3s-Z" % self.id)

        return query

    @classmethod
    def find(cls, **kwargs):
        q = cls.all()
        for k, v in kwargs.items():
            q.filter("%s =" % k, v)

        return q.get()
