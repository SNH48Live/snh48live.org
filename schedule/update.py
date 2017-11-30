#!/usr/bin/env python3

import argparse
import hashlib
import json
import logging
import multiprocessing.pool
import os
import re
import time

import arrow
import attrdict
import peewee
import requests

from common import DATAFILE, IMAGEDIR, Entry, archive, install_rotating_file_handler, safe_open

logger = logging.getLogger('snh48live-schedule')
install_rotating_file_handler(logger, 'updater.log')

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

# group_id's as used by Pocket 48:
# - All: 0
# - SNH48: 10
# - BEJ48: 11
# - GNZ48: 12
# - SHY48: 13
# - CKG48: 14
#
# Returns a list of entries each of which looks like
#
# {
#   "liveId": "58f6d89d0cf25cce6468bb81",
#   "title": "《美丽世界》剧场公演",
#   "subTitle": "TEAM HII剧场公演",
#   "picPath": "/mediasource/live/14927442546691TlMjBZcE9.jpg",
#   "isOpen": false,
#   "startTime": 1493205300000,
#   "count": {
#     "praiseCount": 292,
#     "commentCount": 9,
#     "memberCommentCount": 0,
#     "shareCount": 8,
#     "quoteCount": 0
#   },
#   "isLike": false,
#   "groupId": 10
# }
#
# Returns None when the request fails.
def fetch_group_schedule(group_id):
    url = 'https://plive.48.cn/livesystem/api/live/v1/openLivePage'
    payload = {'groupId': group_id, 'type': 0, 'limit': 20}
    # Printable version of request, used in logging
    request_str = 'POST %s %s' % (url, json.dumps(payload))
    logger.debug(request_str)
    try:
        resp = requests.post(url, json=payload, timeout=16)
        if resp.status_code != 200:
            logger.error('%s: HTTP %d %s', request_str, resp.status_code, resp.reason)
            return None
    except Exception as e:
        logger.error('%s: %s: %s', request_str, type(e).__name__, e)
        return None
    return list(attrdict.AttrDict(resp.json()).content.liveList)

def update():
    logger.info('updating...')

    api_all_good = True
    # SNH48
    entries = fetch_group_schedule(10)
    if entries is None:
        api_all_good = False
        raw_entries = []
    else:
        raw_entries = entries
    # BEJ48, GNZ48, SHY48
    keywords = re.compile(r'SNH|7SENSES|TEAM ?([SNH]II(?!I)|X(II)?)', re.I)
    for group_id in 11, 12, 13, 14:
        # Sniff out entries that contain SNH and/or 7SENSES
        entries = fetch_group_schedule(group_id)
        if entries is None:
            api_all_good = False
        else:
            raw_entries += [entry for entry in entries
                            if keywords.match(entry.title) or keywords.match(entry.subTitle)]
    raw_entries.sort(key=lambda entry: entry.startTime)

    # Parse raw entries as returned by the API
    entries = []
    download_tasks = []
    for entry in raw_entries:
        live_id = entry.liveId
        title = entry.title.strip()
        subtitle = entry.subTitle.strip()
        timestamp = entry.startTime
        datetime = arrow.get(timestamp / 1000).to('Asia/Shanghai')
        group_id = entry.groupId
        if group_id == 10:
            platform = 'live.snh48.com'
            stream_path_suffix = '9999'
        elif group_id == 11:
            platform = 'live.bej48.com'
            stream_path_suffix = '2001'
        elif group_id == 12:
            platform = 'live.gnz48.com'
            stream_path_suffix = '3001'
        elif group_id == 13:
            platform = 'live.shy48.com'
            stream_path_suffix = '6001'
        elif group_id == 14:
            platform = 'live.ckg48.com'
            stream_path_suffix = '8001'
        else:
            raise NotImplementedError('unrecgonized groupId %s: %s' % (group_id, entry))
        steam_path = 'http://ts.snh48.com/vod/z1.chaoqing.%s/%s/%s.mp4/playlist.m3u8' % (
            stream_path_suffix, datetime.strftime('%Y%m%d'), live_id,
        )
        thumbnail_url = 'https://source1.48.cn%s' % entry.picPath
        image_filename = '%s-%s.jpg' % (datetime.strftime('%Y%m%d%H%M%S'), live_id)
        entries.append({
            'live_id': live_id,
            'title': title,
            'subtitle': subtitle,
            'timestamp': timestamp,
            'datetime': datetime.isoformat(),
            'platform': platform,
            'stream_path': steam_path,
            'thumbnail_url': thumbnail_url,
            'local_filename': image_filename,
        })
        image_path = os.path.join(IMAGEDIR, image_filename)
        if not os.path.isfile(image_path):
            download_tasks.append((thumbnail_url, image_path))

    # Write database.
    #
    # Do not write if DATAFILE already exists and entries are empty,
    # unless all API requests were successful, indicating a legit empty
    # schedule.
    if not os.path.exists(DATAFILE) or entries or api_all_good:
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

    # Insert entries into archival database
    if entries:
        peewee.InsertQuery(Entry, rows=entries).upsert().execute()

def main():
    update()

if __name__ == '__main__':
    main()
