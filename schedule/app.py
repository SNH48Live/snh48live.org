#!/usr/bin/env python3

import atexit
import collections
import json
import multiprocessing
import os
import shutil
import tempfile

import arrow
import attrdict
import babel.dates
import flask

from common import DATAFILE, Entry, IMAGEDIR, install_rotating_file_handler, safe_open

app = flask.Flask(__name__)

app.config['JSON_SORT_KEYS'] = False

def load_scheduled_entries():
    with safe_open(DATAFILE, 'r') as fp:
        try:
            return [attrdict.AttrDict(entry) for entry in json.load(fp)] if fp is not None else []
        except json.JSONDecodeError:
            app.logger.error('failed to parse %s as JSON', DATAFILE)
            flask.abort(500)

def load_past_entries(days=8, excluded_live_ids=None):
    if excluded_live_ids is None:
        excluded_live_ids = ()
    # Note that timestamps in the database are in milliseconds
    now = arrow.get().timestamp * 1000
    x_days_ago = now - 86400 * days * 1000
    return [
        entry for entry in Entry.select().where(
            (Entry.timestamp > x_days_ago) & (Entry.timestamp < now)
        ) if entry.live_id not in excluded_live_ids
    ]

def load_entries():
    scheduled_entries = load_scheduled_entries()
    past_entries = load_past_entries(
        excluded_live_ids=[entry.live_id for entry in scheduled_entries]
    )
    return scheduled_entries, past_entries

def serializable_entries(entries):
    return [
        collections.OrderedDict([
            ('datetime', entry.datetime),
            ('timestamp', entry.timestamp),
            ('title', entry.title),
            ('subtitle', entry.subtitle),
            ('platform', entry.platform),
            ('live_id', entry.live_id),
            ('thumbnail_url', entry.thumbnail_url),
            ('local_thumbnail_url', flask.url_for('image', filename=entry.local_filename)),
        ]) for entry in entries
    ]

@app.template_filter('static')
def static(file):
    return flask.url_for('static', filename=file)

@app.template_filter('strftime')
def strftime(timestamp):
    dt = arrow.get(timestamp / 1000).to('Asia/Shanghai').datetime
    return (babel.dates.format_date(dt, format='full', locale='zh_CN') + ' ' +
            dt.strftime('%H:%M'))

@app.template_filter('hasstandalonemp4')
def hasstandalonemp4(m3u8_url):
    return m3u8_url.endswith('/playlist.m3u8')

@app.template_filter('standalonemp4url')
def standalonemp4url(m3u8_url):
    return m3u8_url[:-14]

@app.route('/')
def index():
    scheduled_entries, past_entries = load_entries()
    return flask.render_template('index.html',
                                 entries=scheduled_entries,
                                 past_entries=reversed(past_entries))

# Alternatively, we can configure the underlying webserver to serve the images directory directly
@app.route('/images/<filename>')
def image(filename):
    with safe_open(os.path.join(IMAGEDIR, filename), 'rb') as fp:
        if fp is None:
            flask.abort(404)
        else:
            return flask.send_from_directory(IMAGEDIR, filename)

@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/x-icon',
    )

@app.route('/proxy/<path:url>')
def proxy(url):
    import re
    import requests

    # Only proxy HEAD requests
    if flask.request.method != 'HEAD':
        return '', 405

    # Accept https://, https:/ (single slash, since Apache collapses
    # multiple slashes in the path), or no scheme at all.
    m = re.match(r'^(?:https?://?)?(ts\.snh48\.com/.*)$', url)
    if not m:
        return 'URL not supported.\n', 400
    url = 'http://%s' % m.group(1)

    try:
        origin_response = requests.head(url)
    except (requests.exceptions.RequestException, OSError):
        return 'HEAD %s failed\n' % url, 500

    response = flask.make_response('', origin_response.status_code)
    for key, val in origin_response.headers.items():
        response.headers[key] = val
    return response

@app.route('/json/')
def structured():
    scheduled_entries, past_entries = load_entries()
    return flask.jsonify(collections.OrderedDict([
        ('scheduled', serializable_entries(scheduled_entries)),
        ('past', serializable_entries(past_entries)),
    ]))

# @app.route('/vods/')
# def vods():
#     import time
#     from common import Entry
#
#     entries = list(Entry.select().where(Entry.timestamp < time.time() * 1000).
#                    order_by(Entry.timestamp.desc()).limit(5))
#     return flask.render_template('vods.html', entries=entries)

@app.errorhandler(404)
def not_found(e):
    return flask.render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return flask.render_template('500.html'), 500

def init():
    install_rotating_file_handler(app.logger, 'server.log')

if __name__ == '__main__':
    init()
    app.jinja_env.auto_reload = True
    app.run(debug=True, threaded=True)
