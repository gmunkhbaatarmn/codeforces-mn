import nose
import parse as _
from nose.tools import eq_ as eq
from nose.tools import ok_ as ok


def test_contest():
    contests = _.cf_api("contest.list")
    ok(all(["id" in c for c in contests]))
    ok(all(["name" in c for c in contests]))
    ok(all(["startTimeSeconds" in c for c in contests]))


def test_problemset():
    problems = _.problemset_problems()
    ok([all(["index" in p for p in problems])])
    ok([all(["name" in p for p in problems])])
    ok([all(["contestId" in p for p in problems])])


def test_problem():
    p = _.problem("10-A")
    eq(p["input"], "standard input")
    eq(p["output"], "standard output")
    eq(p["memory"], "256 megabytes")
    eq(p["time"], "1 second")
    eq(p["tests"][0], ("1 3 2 1 5 10\n0 10\n", "30"))
    eq(p["tests"][1], ("2 8 4 2 5 10\n20 30\n50 100\n", "570"))


def test_problem_sample_test():
    " Parse sample test "
    import cgi

    p = _.problem("48-H")
    eq(p["tests"][0], ("2 2\n0 0 4\n", "\\../\n#\\/#\n\\##/\n.\\/.\n"))
    eq(p["tests"][1], ("2 3\n1 2 3\n", "###/\\#\n##/..\\\n#/....\n/.....\n"))

    p = _.problem("141-E")
    eq(p["tests"][0][1], "0\n\n")

    p = _.problem("101-A")
    eq(p["tests"][2][1], "0\n\n")

    p = _.problem("223-A")
    eq(p["tests"][1][1], "0\n\n")

    p = _.problem("51-B")
    eq(p["tests"][0][0], cgi.escape("<table><tr><td></td></tr></table>\n"))


if __name__ == "__main__":
    argv = [
        __file__,         # run tests of current file
        "--stop",         # stop on first fail
        "--nocapture",    # `print` immediately. (useful for debugging)
        "--quiet",        # disable dotted progress indicator
    ]

    nose.main(argv=argv)
