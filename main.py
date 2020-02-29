from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os
import asyncio

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
API_KEY = os.environ['YOUTUBE_API_KEY']

API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # リクエストボディを取得
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        # 署名を検証し、問題なければhandleに定義されている関数を呼び出す
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    if (event.message.text.startswith('検索')):

        queryWord = event.message.text.lstrip('検索')
        channels = youtube_search(queryWord, 5)

        if (channels.count != 0):
            send_text = "Channels:\n" + "\n".join(channels) + "\n"
        else:
            send_text = "帰れ"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=send_text))

def youtube_search(queryWord, maxResults):
    
    # youtubeのインスタンスを作成
    youtube = build(API_SERVICE_NAME, API_VERSION, developerKey=API_KEY)

    # レスポンスの実行
    search_response = youtube.search().list(
        q=queryWord,
        part="id,snippet",
        maxResults=maxResults
    ).execute()

    channels = []

    # レスポンスの内容を取得してチャンネルだけを保存
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#channel":
            channels.append("%s (%s)" % (search_result["snippet"]["title"], "https://www.youtube.com/channel/" + search_result["id"]["channelId"]))

    return channels

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)