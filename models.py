from natrix import db


class Problem(db.Model):
    contest_id = db.IntegerProperty()
    problem_id = db.StringProperty()
    title = db.StringProperty()
    content = db.TextProperty()
    markdown = db.TextProperty()
    credits = db.StringProperty()

    def code(self, separator=""):
        return "%s%s%s" % (self.contest_id, separator, self.problem_id)

    @property
    def link(self):
        return "/problemset/problem/%s" % self.code("/")
