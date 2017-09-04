#!/usr/bin/env python3

import hashlib
import json
import os
import re

import flask
import flask_sqlalchemy
import flask_restless
import werkzeug.contrib.cache
import requests

app = flask.Flask(__name__)

CACHE_TIMEOUT=60
try:
    cache = werkzeug.contrib.cache.MemcachedCache(['127.0.0.1:11211'], default_timeout=CACHE_TIMEOUT,
                                                  key_prefix='snh48live-filter')
    cache.get('test')  # Test connection
except Exception:
    cache = werkzeug.contrib.cache.SimpleCache(default_timeout=CACHE_TIMEOUT)

# Monkeypatch flask_restless.ProcessingException and flask_restless.views.catch_processing_exceptions.
# This serves two purposes:
# 1. Stop dumping tracebacks to logs;
# 2. Allow a bolted-on caching mechanism through early exit with ProcessingException.
# Kudos to https://gist.github.com/mmautner/cd60fdd45934e5aa494d for the hack.

# https://github.com/jfinkels/flask-restless/blob/0.17.0/flask_restless/views.py#L85-L103
import werkzeug.exceptions
class MonkeypatchProcessingException(werkzeug.exceptions.HTTPException):
    def __init__(self, description='', response=None, code=400, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = code
        self.description = description
        self.response = response

flask_restless.ProcessingException = MonkeypatchProcessingException

# https://github.com/jfinkels/flask-restless/blob/0.17.0/flask_restless/views.py#L149-L163
import functools
def monkeypatch_catch_processing_exceptions(func):
    @functools.wraps(func)
    def decorator(*args, **kw):
        try:
            return func(*args, **kw)
        except flask_restless.ProcessingException as exception:
            status = exception.code
            if exception.response is not None:
                return flask.jsonify(exception.response), status
            else:
                message = exception.description or str(exception)
                return flask.jsonify(message=message), status
    return decorator

# https://github.com/jfinkels/flask-restless/blob/0.17.0/flask_restless/views.py#L526
flask_restless.views.API.decorators[-1] = monkeypatch_catch_processing_exceptions

# API

HERE = os.path.dirname(os.path.realpath(__file__))
DBPATH = os.path.join(HERE, 'data.db')
app.config.update(
    JSON_AS_ASCII=False,
    SQLALCHEMY_DATABASE_URI='sqlite:///%s' % DBPATH,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    TEMPLATES_AUTO_RELOAD=True,
    # This config variable controls development/production mode
    DEVEL=os.getenv('DEVEL'),
)
db = flask_sqlalchemy.SQLAlchemy(app)

class Performance(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Unicode)
    team = db.Column(db.Unicode)
    stage = db.Column(db.Unicode)
    special = db.Column(db.Boolean)
    video_id = db.Column(db.Unicode, unique=True, nullable=True)
    performers = db.Column(db.Unicode)
    live_id = db.Column(db.Unicode, unique=True, nullable=True)
    snh48club_video_id = db.Column(db.Unicode, unique=True, nullable=True)

db.create_all()

def cache_key():
    return hashlib.md5(flask.request.full_path.encode('utf-8')).hexdigest()

def caching_preprocessor(**kwargs):
    key = cache_key()
    cached_result = cache.get(key)
    if cached_result:
        raise flask_restless.ProcessingException(response=json.loads(cached_result), code=200)

def caching_postprocessor(result, **kwargs):
    cache.set(cache_key(), json.dumps(result))

YEAR_PATTERN = re.compile('^\d{4}$')

def pre_get_many(search_params=None, **kwargs):
    if search_params is None:
        search_params = {}
    if not search_params.get('order_by'):
        # Impose the default reverse-chronological order if order_by is not explicitly given.
        search_params['order_by'] = [{'field': 'id', 'direction': 'desc'}]

    if 'filters' not in search_params:
        search_params['filters'] = []
    query_params = flask.request.args

    if len(query_params.getlist('year')) > 1:
        raise flask_restless.ProcessingException(description='More than one year specified.')
    year = query_params.get('year')
    if year:
        if not YEAR_PATTERN.match(year):
            raise flask_restless.ProcessingException(description="Invalid year '{}'.".format(year))
        search_params['filters'].append(dict(name='title', op='like', val='{}%'.format(year)))

    if len(query_params.getlist('team')) > 1:
        raise flask_restless.ProcessingException(description='More than one team specified.')
    team = query_params.get('team')
    if team:
        search_params['filters'].append(dict(name='team', op='==', val=team))

    if len(query_params.getlist('stage')) > 1:
        raise flask_restless.ProcessingException(description='More than one stage specified.')
    stage = query_params.get('stage')
    if stage:
        if stage == 'special':
            search_params['filters'].append(dict(name='special', op='==', val=True))
        else:
            search_params['filters'].append(dict(name='stage', op='==', val=stage))

    if len(query_params.getlist('member')) > 1:
        raise flask_restless.ProcessingException(description='More than one member specified.')
    member = query_params.get('member')
    if member:
        search_params['filters'].append(dict(name='performers', op='like', val='%{},%'.format(member)))

# Disable single resource requests
def pre_get_single(instance_id=None, **kwargs):
    raise flask_restless.ProcessingException(description='Single resource requests disabled.')

manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(
    Performance,
    methods=['GET'],
    results_per_page=10,
    max_results_per_page=100,
    preprocessors={
        'GET_MANY': [pre_get_many, caching_preprocessor],
        'GET_SINGLE': [pre_get_single],
    },
    postprocessors={
        'GET_MANY': [caching_postprocessor],
    },
)

# Site

TEAM_DISPLAY_NAMES = {
    's2': 'SⅡ',
    'n2': 'NⅡ',
    'h2': 'HⅡ',
    'x': 'X',
    'x2': 'XⅡ',
}

STAGE_DISPLAY_NAMES = {
    'special': '特别公演',
}

@app.route('/')
def index():
    query_params = flask.request.args
    team = query_params.get('team')
    stage = query_params.get('stage')
    member = query_params.get('member')
    constraints = list(filter(bool, (
        TEAM_DISPLAY_NAMES.get(team),
        STAGE_DISPLAY_NAMES.get(stage, stage),
        member,
    )))
    title = 'SNH48公演检索'
    if constraints:
        title += '（%s）' % ('，'.join(constraints))
    return flask.render_template('index.html', title=title)

@app.route('/about')
def about():
    return flask.render_template('about.html')

YOUTUBE_SLUG = re.compile(r'^[a-zA-Z0-9_-]{11}$')
SNH48CLUB_SLUG = re.compile(r'^club:(?P<snh48club_video_id>\d+)$')

@app.route('/performance/<slug>')
def performance(slug):
    if YOUTUBE_SLUG.match(slug):
        video_id = slug
        entry = db.session.query(Performance).filter_by(video_id=video_id).first()
    else:
        m = SNH48CLUB_SLUG.match(slug)
        if m:
            snh48club_video_id = m.group('snh48club_video_id')
            entry = db.session.query(Performance).filter_by(snh48club_video_id=snh48club_video_id).first()
        else:
            flask.abort(404)

    if not entry:
        flask.abort(404)

    youtube_link = ('https://youtu.be/%s' % entry.video_id) if entry.video_id else None
    title = re.sub(r'^(\d{8}) SNH48 ', '\g<1> ', entry.title)
    imgsrc = (('https://i.ytimg.com/vi/%s/mqdefault.jpg' % entry.video_id) if entry.video_id
              else flask.url_for('static', filename='unavailable.jpg'))
    performers = entry.performers.split(',')[:-1]

    data = dict(
        youtube_link=youtube_link,
        title=title,
        imgsrc=imgsrc,
        performers=performers,
    )
    return flask.render_template('performance.html', **data)

# Update webhook

DATAURL = 'https://raw.githubusercontent.com/SNH48Live/SNH48Live/master/data/performances.json'

def reset():
    db.session.query(Performance).delete()
    db.session.commit()
    cache.clear()

def update():
    resp = requests.get(DATAURL, stream=True)
    if resp.status_code != 200:
        message = 'GET %s: HTTP %d' % (DATAURL, resp.status_code)
        return flask.jsonify(dict(message=message)), 500

    new_records = []
    performances = []
    for line in resp.iter_lines(decode_unicode=True):
        obj = json.loads(line)
        if db.session.query(Performance).filter_by(**obj).first():
            # Hitting existing records
            break
        else:
            new_records.append(obj)
            performances.append(Performance(**obj))
    resp.close()
    # Note that records appearing earlier in the stream should be inserted later
    db.session.bulk_save_objects(reversed(performances))
    db.session.commit()
    cache.clear()
    return flask.jsonify(dict(message='Success', new_records=new_records)), 200

@app.route('/webhook/update', methods=['POST'])
def update_hook():
    return update()

@app.route('/webhook/reset', methods=['POST'])
def reset_hook():
    reset()
    return update()

if __name__ == '__main__':
    app.run(debug=True)
