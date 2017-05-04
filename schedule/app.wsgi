import glob
import os
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.dirname(HERE)
# Look for site-packages first in venv, then in ../venv, and use the first one.
VENVLIB = (glob.glob('%s/venv/lib/python3.*/site-packages' % HERE) +
           glob.glob('%s/venv/lib/python3.*/site-packages' % ROOT))[0]
sys.path.insert(0, VENVLIB)
sys.path.insert(0, HERE)

from app import init
from app import app as application

init()

# Local Variables:
# mode: python
# End:
