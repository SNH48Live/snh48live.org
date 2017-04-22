#!/usr/bin/env python3

import contextlib
import fcntl
import logging
import logging.handlers
import os

HERE = os.path.dirname(__file__)

DATADIR = os.path.join(HERE, 'data')
os.makedirs(DATADIR, exist_ok=True)
DATAFILE = os.path.join(DATADIR, 'data.json')

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

# Safe file access with advisory locks.
# mode is either 'r' for read or 'w' for write.
@contextlib.contextmanager
def safe_open(path, mode):
    if mode not in ('r', 'w'):
        raise NotImplementedError('%s is not a supported mode' % mode)
    flags = os.O_RDONLY if mode == 'r' else (os.O_CREAT | os.O_WRONLY)
    try:
        fd = os.open(path, flags, mode=0o600)
    except OSError:
        yield None
        return
    fcntl.flock(fd, fcntl.LOCK_EX)
    fp = os.fdopen(fd, mode)
    yield fp
    fcntl.flock(fd, fcntl.LOCK_UN)
    fp.close()
