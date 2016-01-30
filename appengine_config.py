"""
`appengine_config.py` is automatically loaded when Google App Engine
starts a new instance of your application. This runs before any
WSGI applications specified in app.yaml are loaded.
"""

import sys
from glob import glob
from google.appengine.ext import vendor


vendor.add("packages")
sys.path.extend(glob("packages/*.zip"))
