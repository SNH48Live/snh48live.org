#!/usr/bin/env python3

import json
import os
import time

import attrdict
import requests
import setproctitle

from common import appname, datafile, safe_open

UPDATE_INTERVAL = 1800

def update():
    # TODO: set up logging
    # logger.info('updating...')
    url = 'https://plive.48.cn/livesystem/api/live/v1/openLivePage'
    payload = {'groupId': 10, 'type': 0}
    resp = requests.post(url, json=payload)
    if resp.status_code != 200:
        # TODO: set up logging
        # logger.warning('failed to fetch schedule data: HTTP %d %s', resp.status_code, resp.reason)
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
    with safe_open(datafile(), 'w') as fp:
        json.dump(entries, fp)

def periodic_updater():
    try:
        setproctitle.setproctitle('%s_updater' % appname)
        while True:
            time.sleep(UPDATE_INTERVAL - time.time() % UPDATE_INTERVAL)
            update()
    except KeyboardInterrupt:
        pass
