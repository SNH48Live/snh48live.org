#!/usr/bin/env python3

import hashlib
import json
import logging
import multiprocessing.pool
import os
import time

import arrow
import attrdict
import daemonize
import requests
import setproctitle

from common import DATAFILE, IMAGEDIR, install_rotating_file_handler, safe_open

UPDATE_INTERVAL = 1800

XDG_RUNTIME_DIR = os.getenv('XDG_RUNTIME_DIR')
RUNTIME_DIR = os.path.join(XDG_RUNTIME_DIR if XDG_RUNTIME_DIR else '/tmp', 'snh48schedule')
os.makedirs(RUNTIME_DIR, exist_ok=True)
PIDFILE = os.path.join(RUNTIME_DIR, 'updater.pid')

logger = logging.getLogger('snh48schedule_updater')
install_rotating_file_handler(logger, 'updater.log')

def md5sum(s):
    m = hashlib.md5()
    m.update(s.encode('utf-8'))
    return m.hexdigest()

def download(url, path):
    resp = requests.get(url, stream=True)
    if resp.status_code != 200:
        raise RuntimeError('HTTP %d %s' % (resp.status_code, resp.reason))
    with safe_open(path, 'wb') as fp:
        for chunk in resp.iter_content(1024):
            fp.write(chunk)

def download_with_retry(url, path):
    logger.info('downloading %s to %s', url, path)
    retry_interval = 1
    while True:
        try:
            download(url, path)
            break
        except Exception as e:
            logger.error('failed to download %s: %s: %s; retrying in %d',
                         url, type(e).__name__, e, retry_interval)
            time.sleep(retry_interval)
            # Exponential backoff
            retry_interval *= 2
            if retry_interval > 30:
                retry_interval = 30
        except KeyboardInterrupt:
            break

def update():
    logger.info('updating...')
    setproctitle.setproctitle('snh48schedule_downloader')
    url = 'https://plive.48.cn/livesystem/api/live/v1/openLivePage'
    payload = {'groupId': 10, 'type': 0}
    resp = requests.post(url, json=payload)
    if resp.status_code != 200:
        logger.error('failed to fetch schedule data: HTTP %d %s', resp.status_code, resp.reason)
        return
    data = attrdict.AttrDict(resp.json())

    # Parse API response
    entries = []
    download_tasks = []
    for entry in data.content.liveList:
        title = entry.title.strip()
        subtitle = entry.subTitle.strip()
        timestamp = entry.startTime
        thumbnail_url = 'https://source.48.cn%s' % entry.picPath
        image_filename = '%s-%s.jpg' % (
            arrow.get(timestamp / 1000).to('Asia/Shanghai').strftime('%Y%m%d%H%M%S'),
            md5sum(thumbnail_url),
        )
        entries.append({
            'title': title,
            'subtitle': subtitle,
            'timestamp': timestamp,
            'thumbnail_url': thumbnail_url,
            'local_filename': image_filename,
        })
        image_path = os.path.join(IMAGEDIR, image_filename)
        if not os.path.isfile(image_path):
            download_tasks.append((thumbnail_url, image_path))

    # Write database
    with safe_open(DATAFILE, 'w') as fp:
        json.dump(entries, fp)

    # Download images if necessary
    if download_tasks:
        worker_count = min(len(download_tasks), max(os.cpu_count() * 2, 4))
        with multiprocessing.pool.Pool(processes=worker_count, maxtasksperchild=1) as pool:
            for task in download_tasks:
                pool.apply_async(download_with_retry, task)
            pool.close()
            pool.join()

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
