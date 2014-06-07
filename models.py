from natrix import db
from markdown2 import markdown


class Problem(db.Model):
    code = db.StringProperty()
    title = db.StringProperty()
    markdown = db.TextProperty()
    credits = db.StringProperty()

    @property
    def link(self):
        return "/problemset/problem/%s" % self.code.replace("-", "/")

    @property
    def content(self):
        return markdown(self.markdown, extras=["code-friendly"])

    @property
    def index(self):
        return self.code.split("-")[1]

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
