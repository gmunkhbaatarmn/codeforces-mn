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
