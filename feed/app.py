#!/usr/bin/env python3

import attrdict
import feedgen.feed
import flask
import flask_cache
import jinja2

import api

app = flask.Flask(__name__)
cache = flask_cache.Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 600,
})
youtube = api.get_authenticated_service()

@cache.cached()
@app.route('/')
def feed():
    feed_url = flask.request.url_root
    fg = feedgen.feed.FeedGenerator()
    fg.id(feed_url)
    fg.title('SNH48 Live')
    fg.subtitle('SNH48公演录播')
    fg.author({'name': 'SNH48Live', 'email': 'snh48live@gmail.com'})
    fg.link(href=feed_url, rel='self', type='application/atom+xml')
    fg.link(href='https://www.youtube.com/SNH48Live', rel='alternate', type='text/html')
    fg.logo('https://snh48live.org/static/logo.png')
    fg.language('zh-cmn-Hans-CN')
    content_template = jinja2.Template('''\
    <p><img src="{{ thumbnail_url }}" alt="{{ video_url }}"></p>
    {%- for line in description.split('\n') -%}
    {%- if line -%}<p>{{ line|urlize }}</p>{%- endif -%}
    {%- endfor -%}''')
    for video in api.list_videos(youtube):
        video = attrdict.AttrDict(video).snippet
        video_id = video.resourceId.videoId
        video_url = 'https://youtu.be/%s' % video.resourceId.videoId
        fe = fg.add_entry()
        fe.id(video_url)
        fe.link(href=video_url, rel='alternate', type='text/html')
        fe.title(video.title)
        fe.published(video.publishedAt)
        fe.updated(video.publishedAt)
        fe.content(content_template.render(
            thumbnail_url=video.thumbnails.maxres.url,
            video_url=video_url,
            description=video.description,
        ), type='html')
    return flask.Response(fg.atom_str(pretty=True), mimetype='application/xml')

if __name__ == '__main__':
    app.run(debug=True)
