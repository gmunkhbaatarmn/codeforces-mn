import nose
import parse as _
from nose.tools import eq_ as eq
from nose.plugins.attrib import attr


def test_contest():
    eq(_.contest(433), {
        "name": "Codeforces Round #248 (Div. 2)",
        "problems": [
            ("A", "Kitahara Haruki's Gift"),
            ("B", "Kuriyama Mirai's Stones"),
            ("C", "Ryouko's Memory Note"),
            ("D", "Nanami's Digital Board"),
            ("E", "Tachibana Kanade's Tofu"),
        ],
    })
    eq(_.contest(1000), None)
    eq(_.contest(0), None)


def test_problemset():
    eq(_.problemset(23)[-1], ["1A", "Theatre Square"])


def test_problem():
    p = _.problem("10-A")
    eq(p["input"], "standard input")
    eq(p["output"], "standard output")
    eq(p["memory"], "256 megabytes")
    eq(p["time"], "1 second")
    eq(p["tests"][0], ("1 3 2 1 5 10\n0 10", "30"))
    eq(p["tests"][1], ("2 8 4 2 5 10\n20 30\n50 100", "570"))


@attr("focus")
def test_problem_sample_test():
    " Parse sample test "
    import cgi

    p = _.problem("48-H")
    eq(p["tests"][0], ("2 2\n0 0 4", "\\../\n#\\/#\n\\##/\n.\\/."))
    eq(p["tests"][1], ("2 3\n1 2 3", "###/\\#\n##/..\\\n#/....\n/....."))

    p = _.problem("141-E")
    eq(p["tests"][0][1], "0\n")

    p = _.problem("101-A")
    eq(p["tests"][2][1], "0\n")

    p = _.problem("223-A")
    eq(p["tests"][1][1], "0\n")

    p = _.problem("51-B")
    eq(p["tests"][0], (cgi.escape("<table><tr><td></td></tr></table>"), "1 "))

    p = _.problem("522-C")
    eq(p["tests"][0][0], ("2\n\n3 4\n2 3 2 1\n1 0\n0 0\n\n5 5\n"
                          "1 2 1 3 1\n3 0\n0 0\n2 1\n4 0"))

    '''
    import re
    import time
    import multiprocessing

    def confirm(code):
        old = _.problem_old(code)
        new = _.problem_new(code)

        if old["tests"] == new["tests"]:
            print "%5s: PASSED" % code
            return
        print "%5s" % code
        print "--------------------------------------"
        print old["tests"]
        print "--------------------------------------"
        print new["tests"]
        print "======================================"

    for page in range(23, 0, -1):
        for code, __ in reversed(_.problemset(page)):
            code = "%s-%s" % re.search("(\s*\d+)(.+)", code).groups()
            if code in ["524-A", "524-B"]:
                continue

            while True:
                start = time.time()
                p = multiprocessing.Process(target=confirm, args=(code,))
                p.start()

                success = True
                while p.is_alive():
                    if start + 10.0 < time.time():
                        success = False
                        break
                    time.sleep(0.1)

                if success:
                    break

                # Terminate
                print "Delayed: %s" % code
                p.terminate()
                p.join()
    '''


if __name__ == "__main__":
    argv = [
        __file__,         # run tests of current file
        "--stop",         # stop on first fail
        "--nocapture",    # `print` immediately. (useful for debugging)
        "--quiet",        # disable dotted progress indicator
        "--attr=focus",   # run focused tests
    ]

    nose.main(argv=argv)
