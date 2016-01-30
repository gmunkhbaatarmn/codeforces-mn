from natrix import Model, db, json, warning


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
    id = db.IntegerProperty()
    name = db.StringProperty()
    start_at = db.IntegerProperty()
    problems_json = db.StringProperty()
    translated_count = db.IntegerProperty(default=0)

    @property
    def problems(self):
        # list of tuple (letter, problemset code)
        result = []
        if not self.problems_json:
            # todo: resolve this warning logs
            warning("Contest: %s" % self.id)
        data = json.loads(self.problems_json or "{}")

        for letter, code in sorted(data.items()):
            result.append([letter, code])
        return result

    @property
    def problems_object(self):
        result = []

        for letter, code in sorted(self.problems, key=lambda p: p[0]):
            result.append([letter, Problem.find(code=code)])

        return result
