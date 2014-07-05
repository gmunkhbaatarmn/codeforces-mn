import nose
import parse as _
from nose.tools import eq_ as eq


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
    eq(_.problemset(19)[-1], ["1A", "Theatre Square"])


def test_problem():
    p = _.problem("10-A")
    eq(p["input"], "standard input")
    eq(p["output"], "standard output")
    eq(p["memory"], "256 megabytes")
    eq(p["time"], "1 second")
    eq(p["tests"][0], ("1 3 2 1 5 10\n0 10", "30"))
    eq(p["tests"][1], ("2 8 4 2 5 10\n20 30\n50 100", "570"))


def test_contest_history():
    eq(_.contest_history(1)[1], [])


if __name__ == "__main__":
    nose.main(defaultTest=__file__)
