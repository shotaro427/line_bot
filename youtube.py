import os
from apiclient.discovery import build
from apiclient.errors import HttpError

API_KEY = os.environ['YOUTUBE_API_KEY']
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

def youtube_search(options):
    
    # youtubeのインスタンスを作成
    youtube = build(API_SERVICE_NAME, API_VERSION, developerKey=API_KEY)

    # レスポンスの実行
    search_response = youtube.search().list(
        q=options.q,
        part="id,snippet",
        maxResults=options.max_results
    ).execute()

    channels = []

    # レスポンスの内容を取得してチャンネルだけを保存
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#channel":
            channels.append("%s (%s)" % (search_result["snippet"]["title"], search_result["id"]["channelId"]))

    return channels

