import sys
import nose
import logging
import codeforces
from nose.tools import ok_ as ok
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
def test_codeforces_mongolians():
    progress("codeforces.mongolians")

    handles = codeforces.mongolians()

    ok(len(handles) > 0)
    map(lambda i: isinstance(i, basestring), handles)

    progress("codeforces.mongolians\n")


if __name__ == "__main__":
    argv = [
        __file__,         # run tests of current file
        "--stop",         # stop on first fail
        "--nocapture",    # `print` immediately. (useful for debugging)
        "--quiet",        # disable dotted progress indicator
    ]

    # run focused test: `python tests.py --focus`
    if len(sys.argv) > 1 and sys.argv[1] == "--focus":
        argv.append("--attr=focus")

    nose.main(argv=argv)
