from natrix import db
from markdown2 import markdown


class Problem(db.Model):
    code = db.StringProperty()
    title = db.StringProperty()
    markdown = db.TextProperty()
    credits = db.StringProperty()
    # in_problemset = db.BooleanProperty()

    @property
    def link(self):
        return "/problemset/problem/%s" % self.code.replace("-", "/").strip()

    @property
    def link_contest(self):
        return "/contest/%s/problem/%s" % (self.contest_id, self.index)

    @property
    def content(self):
        return markdown(self.markdown, extras=["code-friendly"])

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


class Contest(db.Model):
    id = db.IntegerProperty()
    name = db.StringProperty()
    start = db.StringProperty()
    # duration = db.IntegerProperty()

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
