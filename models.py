from natrix import Model, db, json


class Suggestion(Model):
    code = db.StringProperty()
    title = db.StringProperty()
    content = db.TextProperty(default="")
    note = db.TextProperty(default="")
    credits = db.StringProperty(default="")
    added = db.DateTimeProperty(auto_now=True)

    @property
    def problem_link(self):
        return "/problemset/problem/%s" % self.code.replace("-", "/").strip()


class Problem(Model):
    code = db.StringProperty()
    title = db.StringProperty()

    content = db.TextProperty(default="")
    note = db.TextProperty(default="")
    credits = db.StringProperty(default="")
    identifier = db.StringProperty()  # unique identifier

    # open graph supports
    og_id = db.IntegerProperty(default=0)

    # time, memory, input, output, tests
    meta_json = db.TextProperty(default="{}")

    @property
    def link(self):
        return "/problemset/problem/%s" % self.code.replace("-", "/").strip()

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
    id = db.IntegerProperty()  # noqa: A003
    name = db.StringProperty()
    start_at = db.IntegerProperty()
    problems_json = db.StringProperty()  # dict of {letter: code}
    translated_count = db.IntegerProperty(default=0)

    @property
    def problems(self):
        problems = json.loads(self.problems_json or "{}")

        return [(k, v) for k, v in sorted(problems.items())]

    @property
    def problems_object(self):
        problems = json.loads(self.problems_json or "{}")

        return [(k, Problem.find(code=v)) for k, v in sorted(problems.items())]
