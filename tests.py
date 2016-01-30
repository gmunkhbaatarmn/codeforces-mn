import sys
import nose
import logging
import topcoder
import codeforces
from nose.tools import ok_ as ok, eq_ as eq
from nose.plugins.attrib import attr
from google.appengine.ext.testbed import Testbed


def setup():
    " Google App Engine testbed configuration "
    progress("setup")

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

    eq(len(codeforces.api("user.info", handles="Petr;tourist")), 2)

    progress("codeforces.api\n")


def test_codeforces_mongolians():
    progress("codeforces.mongolians")

    handles = codeforces.mongolians()

    ok(len(handles) > 0)
    map(lambda i: isinstance(i, basestring), handles)

    progress("codeforces.mongolians\n")


# Module: topcoder
@attr("focus")
def test_topcoder_mongolians():
    progress("topcoder.mongolians")

    handles = topcoder.mongolians()

    ok(len(handles) > 0)
    for handle, id in handles:
        ok(isinstance(handle, basestring))
        ok(isinstance(id, int))

    progress("topcoder.mongolians\n")


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
