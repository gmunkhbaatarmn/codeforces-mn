from natrix import db


class Problem(db.Model):
    code = db.StringProperty()
    title = db.StringProperty()
    content = db.TextProperty()
    markdown = db.TextProperty()
    credits = db.StringProperty()

    @property
    def link(self):
        return "/problemset/problem/%s" % self.code.replace("-", "/")

    @classmethod
    def find(cls, **kwargs):
        q = cls.all()
        for k, v in kwargs.items():
            q.filter("%s =" % k, v)

        return q.get()
