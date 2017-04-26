# [snh48schedule](https://snh48schedule.zhimingwang.org)

[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg?maxAge=31536000)](COPYING)

An extremely simple and usable website for checking SNH48's live streaming schedule. Note that there's already a rolling schedule on the homepage of live.snh48.com, but its usability is beyond horrible.

<https://snh48schedule.zhimingwang.org>

## Requirements

- Python 3.x. I targeted 3.5+ mentally, but it should probably work with 3.4 or even 3.3, too.
- [Web browser with support for CSS grid layout](https://caniuse.com/#feat=css-grid).

## Setting up

### Web server process

For development purposes, simply install the requirements and run

```
./app.py
```

To serve with Apache, install and enable mod_wsgi for Python 3 (`libapache2-mod-wsgi-py3` on Ubuntu/Debian). Set up the `venv` directory as follows:

```
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

then set up the site with `snh48schedule.wsgi`. See [Flask's documentation on mod_wsgi](http://flask.pocoo.org/docs/0.12/deploying/mod_wsgi/). Make sure this directory as well as `data/` and `logs/` (if either exists) are writable by web server processes (e.g. `www-data`).

### Background updater process

The background updater `update.py` needs to be run separately.

```
./update.py
```

kicks off the daemon. A [systemd.service template](snh48schedule_updater.service.template) is provided.

## Todos

See [#1](https://github.com/SNH48Live/snh48schedule/issues/1).
