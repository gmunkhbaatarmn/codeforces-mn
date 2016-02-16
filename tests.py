import sys
import nose
import logging
from nose.tools import ok_ as ok, eq_ as eq
from nose.plugins.attrib import attr
from google.appengine.ext.testbed import Testbed


def setup():
    " Google App Engine testbed configuration "
    progress("setup")
    sys.path.append("./packages")

    # hide `debug`, `info` level logs
    logging.root = logging.RootLogger(logging.WARNING)

    # create an instance of testbed class
    testbed = Testbed()

    # activate the testbed, which prepares the services stub for use
    testbed.activate()

    # declare which stubs want to use
    testbed.init_urlfetch_stub()
    testbed.init_datastore_v3_stub()
    testbed.init_memcache_stub()

    progress("setup\n")


def progress(message):
    reset, green, yellow = "\033[0m", "\033[32m", "\033[33m"

    if message.endswith("\n"):
        message = green + "DONE " + reset + message
    else:
        message = yellow + ".... " + message + reset

    sys.stdout.write("\r" + " " * 150 + "\r")
    sys.stdout.write(message)
    sys.stdout.flush()


# Module: codeforces
def test_codeforces_api():
    progress("codeforces.api")
    import codeforces

    eq(len(codeforces.api("user.info", handles="Petr;tourist")), 2)

    progress("codeforces.api\n")


def test_codeforces_mongolians():
    progress("codeforces.mongolians")
    import codeforces

    handles = codeforces.mongolians()

    ok(len(handles) > 0)
    map(lambda i: isinstance(i, basestring), handles)

    progress("codeforces.mongolians\n")


def test_codeforces_problem():
    progress("codeforces.problem")
    import codeforces

    codeforces.problem(" 51-B")
    codeforces.problem("575-I")
    codeforces.problem("576-E")

    progress("codeforces.problem\n")


def test_codeforces_upcoming_contests():
    progress("codeforces.upcoming_contests")
    import codeforces

    for i in codeforces.upcoming_contests():
        ok(isinstance(i["site"], basestring))
        ok(isinstance(i["name"], basestring))
        ok(isinstance(i["link"], basestring))
        ok(isinstance(i["start_at"], int))

    progress("codeforces.upcoming_contests\n")


# Module: topcoder
def test_topcoder_mongolians():
    progress("topcoder.mongolians")
    import topcoder

    handles = topcoder.mongolians()

    ok(len(handles) > 0)
    for handle, id in handles:
        ok(isinstance(handle, basestring))
        ok(isinstance(id, int))

    progress("topcoder.mongolians\n")


def test_topcoder_user_info():
    progress("topcoder.user_info")
    import topcoder

    u = topcoder.user_info(22833617)

    ok(isinstance(u["active"], bool))
    ok(isinstance(u["contest_id"], int))
    ok(isinstance(u["new_rating"], int))
    ok(isinstance(u["old_rating"], int))

    progress("topcoder.user_info\n")


def test_topcoder_upcoming_contests():
    progress("topcoder.upcoming_contests")
    import topcoder

    for i in topcoder.upcoming_contests():
        ok(isinstance(i["site"], basestring))
        ok(isinstance(i["name"], basestring))
        ok(isinstance(i["link"], basestring))
        ok(isinstance(i["start_at"], int))

    progress("topcoder.upcoming_contests\n")


# Module: opengraph
def test_opengraph_fetch_id():
    progress("opengraph.fetch_id")
    import opengraph

    url = "http://codeforces.mn/problemset/problem/625/E"
    eq(opengraph.fetch_id(url), 1278889565460171)

    progress("opengraph.fetch_id\n")


@attr("focus")
def test_opengraph_fetch_comments():
    progress("opengraph.fetch_comments")
    import opengraph
    ids = [(1278889565460171, "625-E"), (827387507370816, "625-D"),
           (935692406527535, "625-C"), (1019738524749056, "625-B")]
    opengraph.fetch_comments(ids)
    progress("opengraph.fetch_comments\n")


if __name__ == "__main__":
    argv = [
        __file__,         # run tests of current file
        "--stop",         # stop on first fail
        "--nocapture",    # `print` immediately. (useful for debugging)
        "--quiet",        # disable dotted progress indicator
    ]

    # Run focused tests
    """
    Call:
        python tests.py --focus

    Focus on test function:
        @attr("focus")
        def test_ensure_me():
            ok(True)
    """
    if len(sys.argv) > 1 and sys.argv[1] == "--focus":
        argv.append("--attr=focus")
    attr
    # endfold

    nose.main(argv=argv)
