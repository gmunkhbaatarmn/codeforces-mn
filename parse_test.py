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


def test_contest_history():
    eq(_.contest_history(1)[1], [])


if __name__ == "__main__":
    nose.main(defaultTest=__file__)
