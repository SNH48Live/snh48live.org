#!/usr/bin/env python3

import os

import googleapiclient.discovery
import httplib2
import oauth2client.client
import oauth2client.file
import oauth2client.tools

# 全部公演
# https://www.youtube.com/playlist?list=PL0-h3TcYaV9GWj2qGYa1cWgFCP-k3Blaj
PLAYLIST_ID = 'PL0-h3TcYaV9GWj2qGYa1cWgFCP-k3Blaj'

YOUTUBE_READONLY_SCOPE = 'https://www.googleapis.com/auth/youtube.readonly'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

HERE = os.path.dirname(os.path.realpath(__file__))

# Download clients_secrets.json from
#   https://console.developers.google.com/apis/credentials?project=YOUR_PROJECT
# YouTube Data API needs to be enabled for the project.
CLIENT_SECRETS_FILE = os.path.join(HERE, 'client_secrets.json')

# Auto generated.
OAUTH_CREDENTIALS_FILE = os.path.join(HERE, 'credentials.json')

def get_authenticated_service():
    flow = oauth2client.client.flow_from_clientsecrets(
        CLIENT_SECRETS_FILE,
        scope=YOUTUBE_READONLY_SCOPE,
    )

    storage = oauth2client.file.Storage(OAUTH_CREDENTIALS_FILE)
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = oauth2client.tools.run_flow(flow, storage)

    return googleapiclient.discovery.build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        http=credentials.authorize(httplib2.Http()),
    )

# num should be <= 50.
def list_videos(youtube, num=20):
    response = youtube.playlistItems().list(
        part='snippet',
        playlistId=PLAYLIST_ID,
        maxResults=min(num, 50),
    ).execute()
    return response['items']

def main():
    youtube = get_authenticated_service()
    import json
    print(json.dumps(list_videos(youtube), ensure_ascii=False, sort_keys=True, indent=2), end='')

if __name__ == '__main__':
    main()
