import glob
import os
import sys

HERE = os.path.dirname(__file__)
VENVLIB = glob.glob('%s/venv/lib/python3.*/site-packages' % HERE)[0]
sys.path.insert(0, VENVLIB)
sys.path.insert(0, HERE)

from app import init
from app import app as application

init()

# Local Variables:
# mode: python
# End:
