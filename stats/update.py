#!/usr/bin/env python3

# SVG optimization is done via svgo(1) from https://github.com/svg/svgo.

import argparse
import datetime
import logging
import os
import subprocess
import sys
import time

import arrow
import daemonize
import googleapiclient.discovery
import httplib2
import oauth2client.client
import oauth2client.file
import oauth2client.tools
import peewee
import setproctitle

import matplotlib
matplotlib.use('svg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family': 'Consolas', 'font.size': 16})
from matplotlib.ticker import MaxNLocator

import utils

CHANNEL_ID = 'UC10BBCJQasWk_08Fdz0XCsQ'
STARTING_DATE = '2017-03-22' # Channel creation date

YOUTUBE_ANALYTICS_READONLY_SCOPE = 'https://www.googleapis.com/auth/yt-analytics.readonly'
YOUTUBE_ANALYTICS_API_SERVICE_NAME = 'youtubeAnalytics'
YOUTUBE_ANALYTICS_API_VERSION = 'v1'

HERE = os.path.dirname(os.path.realpath(__file__))
DATADIR = os.path.join(HERE, 'data')
os.makedirs(DATADIR, exist_ok=True)

# Download clients_secrets.json from
#   https://console.developers.google.com/apis/credentials?project=YOUR_PROJECT
# YouTube Data API needs to be enabled for the project.
CLIENT_SECRETS_FILE = os.path.join(HERE, 'client_secrets.json')

# Auto generated.
OAUTH_CREDENTIALS_FILE = os.path.join(HERE, 'credentials.json')

DATABASE = os.path.join(HERE, 'analytics.sqlite3')
database = peewee.SqliteDatabase(DATABASE)

logger = logging.getLogger('snh48live-schedule')
utils.install_rotating_file_handler(logger, 'updater.log')

# Update once per day
UPDATE_INTERVAL = 21600

XDG_RUNTIME_DIR = os.getenv('XDG_RUNTIME_DIR')
RUNTIME_DIR = os.path.join(XDG_RUNTIME_DIR if XDG_RUNTIME_DIR else '/tmp', 'snh48live-stats')
os.makedirs(RUNTIME_DIR, exist_ok=True)
PIDFILE = os.path.join(RUNTIME_DIR, 'updater.pid')

class Date(peewee.Model):
    date = peewee.TextField(unique=True)
    subscribers_gained = peewee.IntegerField()
    subscribers_lost = peewee.IntegerField()
    views = peewee.IntegerField()
    estimated_minutes_watched = peewee.IntegerField()

    class Meta:
        database = database

def get_authenticated_service(args=None):
    flow = oauth2client.client.flow_from_clientsecrets(
        CLIENT_SECRETS_FILE,
        scope=YOUTUBE_ANALYTICS_READONLY_SCOPE,
    )

    storage = oauth2client.file.Storage(OAUTH_CREDENTIALS_FILE)
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = oauth2client.tools.run_flow(flow, storage, args)

    return googleapiclient.discovery.build(
        YOUTUBE_ANALYTICS_API_SERVICE_NAME,
        YOUTUBE_ANALYTICS_API_VERSION,
        http=credentials.authorize(httplib2.Http()),
    )

# end_date should be in the form YYYY-MM-DD.
# Returns a tuple of ints (subscribers_gained, subscribers_lost, views, estimated_minutes_watched).
def fetch_cumulated_stats(youtube_analytics, end_date):
    logger.info('fetching accumulated analytics until %s...', end_date)
    # https://developers.google.com/youtube/analytics/v1/channel_reports
    # https://developers.google.com/resources/api-libraries/documentation/youtubeAnalytics/v1/python/latest/youtubeAnalytics_v1.reports.html#query
    response = youtube_analytics.reports().query(
        ids='channel==%s' % CHANNEL_ID,
        start_date='1970-01-01',
        end_date=end_date,
        metrics='subscribersGained,subscribersLost,views,estimatedMinutesWatched',
    ).execute()
    return tuple(map(int, response['rows'][0]))

def optimize_svg(path):
    try:
        temppath = '%s.min' % path
        subprocess.check_call(['svgo', path, temppath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return
    if os.path.isfile(temppath):
        os.rename(temppath, path)

# datapoints should be a list of 60 data points.
# title should be capatalized and will be converted to lower case for the ylabel.
def make_plot(datapoints, title, start_date, end_date, filename=None):
    offsets = range(1, 61)
    plt.figure(figsize=(15, 10))
    plt.title('%s (%s to %s)' % (title, start_date, end_date))
    plt.xlabel('day offset')
    plt.ylabel(title.lower())
    # Hide right and top spines
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    # Force integral ticks on the y-axis
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))

    plt.plot(offsets, datapoints, 'o-', color='#00e600')
    for x, y in zip(offsets, datapoints):
        # Put the actual number on the every 5th point
        if x % 5 == 0:
            plt.text(x, y, str(y), horizontalalignment='center', verticalalignment='bottom')

    if filename is None:
        filename = '%s.svg' % title.lower().replace(' ', '-')
    path = os.path.join(DATADIR, filename)
    with utils.atomic_writer(path, binary=True) as fp:
        plt.savefig(fp)
    optimize_svg(path)

def make_data_plots(data):
    # If there are fewer than 61 data points, insert zeros
    if len(data) < 61:
        data = data.copy()
        date = datetime.datetime.strptime(data[0][0], '%Y-%m-%d').date()
        one_day = datetime.timedelta(days=1)
        while len(data) < 61:
            date -= one_day
            data.insert(0, (date.strftime('%Y-%m-%d'), 0, 0, 0, 0))


    # Plot totals
    dates, subscribers_gained, subscribers_lost, views, estimated_minutes_watched = tuple(zip(*data))
    start_date = dates[1]
    end_date = dates[-1]
    subscribers = [gained - lost for gained, lost in zip(subscribers_gained, subscribers_lost)]
    make_plot(subscribers[1:], 'Total subscribers', start_date, end_date)
    make_plot(views[1:], 'Total views', start_date, end_date)
    make_plot(estimated_minutes_watched[1:], 'Total estimated minutes watched', start_date, end_date)

    # Plot daily growth
    daily_subscribers = [subscribers[i + 1] - subscribers[i] for i in range(60)]
    daily_views = [views[i + 1] - views[i] for i in range(60)]
    daily_estimated_minutes_watched = [estimated_minutes_watched[i + 1] - estimated_minutes_watched[i] for i in range(60)]
    make_plot(daily_subscribers, 'Daily subscribers', start_date, end_date)
    make_plot(daily_views, 'Daily views', start_date, end_date)
    make_plot(daily_estimated_minutes_watched, 'Daily estimated minutes watched', start_date, end_date)

def write_data_csv(data):
    with utils.atomic_writer(os.path.join(DATADIR, 'data.csv')) as fp:
        print('date,subscribers_gained,subscribers_lost,views,estimated_minutes_watched', file=fp)
        for row in data:
            print(','.join(map(str, row)), file=fp)

def update(youtube_analytics):
    logger.info('updating...')

    try:
        # Take the most recent recorded date as starting date.
        # This date is also fetched in case of any updates to the data.
        starting_date = Date.select().order_by(Date.date.desc()).first().date
    except AttributeError:  # Accessing .date of None
        starting_date = STARTING_DATE

    date = datetime.datetime.strptime(starting_date, '%Y-%m-%d').date()
    today = datetime.date.today()
    one_day = datetime.timedelta(days=1)

    data = []
    # The YouTube Analytics lags behind for at least two full days. We
    # only fetch data up to three days before today.
    while date + one_day * 3 <= today:
        date_str = date.strftime('%Y-%m-%d')
        data.append((date_str,) + fetch_cumulated_stats(youtube_analytics, date_str))
        date += one_day

    with database.atomic():
        for date_str, subscribers_gained, subscribers_lost, views, estimated_minutes_watched in data:
            record, created = Date.get_or_create(
                date=date_str,
                defaults=dict(
                    subscribers_gained=subscribers_gained,
                    subscribers_lost=subscribers_lost,
                    views=views,
                    estimated_minutes_watched=estimated_minutes_watched,
                ),
            )
            if not created:
                old_stats = (record.subscribers_gained, record.subscribers_lost,
                             record.views, record.estimated_minutes_watched)
                new_stats = (subscribers_gained, subscribers_lost,
                             views, estimated_minutes_watched)
                if old_stats != new_stats:
                    logger.info('stats changed for %s: %s => %s', date_str, old_stats, new_stats)
                    record.subscribers_gained = subscribers_gained
                    record.subscribers_lost = subscribers_lost
                    record.views = views
                    record.estimated_minutes_watched = estimated_minutes_watched
                    record.save()

    # Select all rows
    data = []
    for record in Date.select().order_by(Date.date):
        data.append((record.date, record.subscribers_gained, record.subscribers_lost,
                     record.views, record.estimated_minutes_watched))
    make_data_plots(data)
    write_data_csv(data)

def periodic_updater():
    setproctitle.setproctitle('snh48live-stats')
    database.connect()
    database.create_tables([Date], safe=True)
    youtube_analytics = get_authenticated_service()
    while True:
        try:
            update(youtube_analytics)
        except Exception as e:
            logger.error('update failed: %s: %s', type(e).__name__, e)
        time.sleep(UPDATE_INTERVAL - time.time() % UPDATE_INTERVAL)

def start_daemon():
    daemon = daemonize.Daemonize(
        app='snh48live-stats',
        pid=PIDFILE,
        action=periodic_updater,
        keep_fds=[handler.stream.fileno() for handler in logger.handlers],
        logger=logger,
    )
    daemon.start()

def main():
    parser = argparse.ArgumentParser(parents=[oauth2client.tools.argparser])
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--authenticate', action='store_true',
                       help='authenticate only (one-time, interactive)')
    group.add_argument('--daemon', action='store_true',
                       help='run in daemon mode (beware of RAM consumption)')
    args = parser.parse_args()

    if args.authenticate:
        get_authenticated_service(args)
        sys.exit(0)

    if args.daemon:
        start_daemon()
    else:
        database.connect()
        database.create_tables([Date], safe=True)
        update(get_authenticated_service())

if __name__ == '__main__':
    main()
