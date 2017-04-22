#!/usr/bin/env python3

import json
import logging
import os
import time

import attrdict
import daemonize
import requests
import setproctitle

from common import DATAFILE, install_rotating_file_handler, safe_open

UPDATE_INTERVAL = 1800

XDG_RUNTIME_DIR = os.getenv('XDG_RUNTIME_DIR')
RUNTIME_DIR = os.path.join(XDG_RUNTIME_DIR if XDG_RUNTIME_DIR else '/tmp', 'snh48schedule')
os.makedirs(RUNTIME_DIR, exist_ok=True)
PIDFILE = os.path.join(RUNTIME_DIR, 'updater.pid')

logger = logging.getLogger('snh48schedule_updater')
install_rotating_file_handler(logger, 'updater.log')

def update():
    logger.info('updating...')
    url = 'https://plive.48.cn/livesystem/api/live/v1/openLivePage'
    payload = {'groupId': 10, 'type': 0}
    resp = requests.post(url, json=payload)
    if resp.status_code != 200:
        logger.warning('failed to fetch schedule data: HTTP %d %s', resp.status_code, resp.reason)
        return
    data = attrdict.AttrDict(resp.json())
    entries = []
    for entry in data.content.liveList:
        entries.append({
            'title': entry.title.strip(),
            'subtitle': entry.subTitle.strip(),
            'timestamp': entry.startTime,
            'thumbnail_url': 'https://source.48.cn%s' % entry.picPath,
        })
    with safe_open(DATAFILE, 'w') as fp:
        json.dump(entries, fp)

def periodic_updater():
    try:
        setproctitle.setproctitle('snh48schedule_updater')
        while True:
            try:
                update()
            except Exception as e:
                logger.error('update failed: %s: %s', type(e).__name__, e)
            time.sleep(UPDATE_INTERVAL - time.time() % UPDATE_INTERVAL)
    except KeyboardInterrupt:
        pass

def start_daemon():
    daemon = daemonize.Daemonize(
        app='snh48schedule_updater',
        pid=PIDFILE,
        action=periodic_updater,
        keep_fds=[handler.stream.fileno() for handler in logger.handlers],
        logger=logger,
    )
    daemon.start()

if __name__ == '__main__':
    start_daemon()
