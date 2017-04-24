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

from common import DATAFILE, IMAGEDIR, install_rotating_file_handler, safe_open

app = flask.Flask(__name__)

@app.template_filter('strftime')
def strftime(timestamp):
    return arrow.get(timestamp / 1000).to('Asia/Shanghai').strftime('%Y-%m-%d %H:%M:%S')

@app.route('/')
def index():
    with safe_open(DATAFILE, 'r') as fp:
        try:
            entries = [attrdict.AttrDict(entry) for entry in json.load(fp)] if fp is not None else []
        except json.JSONDecodeError:
            app.logger.error('failed to parse %s as JSON', DATAFILE)
            flask.abort(500)
    return flask.render_template('index.html', entries=entries)

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

@app.errorhandler(404)
def not_found(e):
    return flask.render_template('404.html'), 404

def init():
    install_rotating_file_handler(app.logger, 'server.log')

if __name__ == '__main__':
    setproctitle.setproctitle('snh48schedule')
    init()
    app.run(debug=True)
