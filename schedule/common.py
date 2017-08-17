#!/usr/bin/env python3

import contextlib
import fcntl
import logging
import logging.handlers
import os

import peewee

HERE = os.path.dirname(os.path.realpath(__file__))

DATADIR = os.path.join(HERE, 'data')
os.makedirs(DATADIR, exist_ok=True)
DATAFILE = os.path.join(DATADIR, 'data.json')
ARCHIVE = os.path.join(DATADIR, 'archive.db')

IMAGEDIR = os.path.join(DATADIR, 'images')
os.makedirs(IMAGEDIR, exist_ok=True)

LOGDIR = os.path.join(HERE, 'logs')
os.makedirs(LOGDIR, exist_ok=True)

archive = peewee.SqliteDatabase(ARCHIVE)

class Entry(peewee.Model):
    live_id = peewee.TextField(unique=True)
    title = peewee.TextField()
    subtitle = peewee.TextField()
    timestamp = peewee.IntegerField()
    datetime = peewee.TextField()
    platform = peewee.TextField()
    stream_path = peewee.TextField()
    thumbnail_url = peewee.TextField()
    local_filename = peewee.TextField()

    class Meta:
        database = archive

archive.create_tables([Entry], safe=True)

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
# Supported modes: r, w, rb, wb.
@contextlib.contextmanager
def safe_open(path, mode):
    if mode not in ('r', 'w', 'rb', 'wb'):
        raise NotImplementedError('%s is not a supported mode' % mode)
    flags = os.O_RDONLY if mode.startswith('r') else (os.O_CREAT | os.O_WRONLY | os.O_TRUNC)
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
