#!/usr/bin/env python3

import contextlib
import logging
import logging.handlers
import os
import random
import string

random = random.SystemRandom()

HERE = os.path.dirname(os.path.realpath(__file__))
LOGDIR = os.path.join(HERE, 'logs')
os.makedirs(LOGDIR, exist_ok=True)

def install_rotating_file_handler(logger, filename, level=logging.INFO, formatter=None,
                                  maxBytes=1048576, backupCount=5):
    if formatter is None:
        formatter = logging.Formatter(fmt='%(asctime)s [%(levelname)s] %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.handlers.RotatingFileHandler(
        os.path.join(LOGDIR, filename),
        maxBytes=maxBytes, backupCount=backupCount
    )
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if not logger.isEnabledFor(level):
        logger.setLevel(level)

# Returns a context manager with a file object that can be written
# to. Content is actually written to a suffixed tempfile, and upon exit
# the tempfile is renamed to the specified file atomically.
@contextlib.contextmanager
def atomic_writer(path, mode=0o640, binary=False):
    suffix = ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
    temppath = '%s.%s' % (path, suffix)
    fd = os.open(temppath, os.O_CREAT | os.O_WRONLY, mode=mode)
    fp = os.fdopen(fd, 'wb' if binary else 'w')
    yield fp
    fp.close()
    os.rename(temppath, path)
