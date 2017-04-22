#!/usr/bin/env python3

import atexit
import json
import multiprocessing
import os
import shutil
import tempfile

import arrow
import attrdict
import flask
import setproctitle

from common import DATAFILE, safe_open
from update import periodic_updater, update

app = flask.Flask(__name__)

@app.template_filter('strftime')
def strftime(timestamp):
    return arrow.get(int(timestamp) / 1000).to('Asia/Shanghai').strftime('%Y-%m-%d %H:%M:%S')

@app.route('/')
def index():
    with safe_open(DATAFILE, 'r') as fp:
        entries = [attrdict.AttrDict(entry) for entry in json.load(fp)]
    return flask.render_template('index.html', entries=entries)

@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/x-icon',
    )

def init():
    update()
    updater_process = multiprocessing.Process(target=periodic_updater)
    updater_process.start()
    return updater_process

if __name__ == '__main__':
    setproctitle.setproctitle('snh48schedule')
    updater_process = init()
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
    updater_process.join()
