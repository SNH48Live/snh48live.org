This app generates an atom feed for the SNH48 Live YouTube channel. It is served at <https://snh48live.org/feed/>.

To run this app, place `client_secrets.json` in this directory and run `./api.py` once to complete the authorization flow. A `credentials.json` will be generated and placed in this directory, with which no further interaction will be required. Make sure `client_secrets.json` is readable by webserver workers, and `credentials.json` is both readable and writable.

The feed is cached server-side. `CACHE_DEFAULT_TIMEOUT` in `app.py` can be tweaked.
