#!/usr/bin/env python3

import contextlib
import fcntl
import os

DATADIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATADIR, exist_ok=True)
DATAFILE = os.path.join(DATADIR, 'data.json')

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
