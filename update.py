#!/usr/bin/env python3

import json
import logging
import os
import time

import attrdict
import requests
import setproctitle

from common import DATAFILE, install_rotating_file_handler, safe_open

UPDATE_INTERVAL = 1800

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
            time.sleep(UPDATE_INTERVAL - time.time() % UPDATE_INTERVAL)
            try:
                update()
            except Exception as e:
                logger.error('update failed: %s: %s', type(e).__name__, e)
    except KeyboardInterrupt:
        pass
