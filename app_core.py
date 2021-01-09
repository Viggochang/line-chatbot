from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError

from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# LINE 聊天機器人的基本資料
line_bot_api = LineBotApi('NpTtgG2aENN8PGBvJQgq986lUDiFeCd5zr2/woya4ELt8J7MefsdLv+VOc+Cja39aV8ii3Hd8+jR8lQHYHlIcDtVKpTbKjPTnl4kQPxuOHZp1pkq2khE8XIhF1XuPKrF3naNuJftXI5cNp6HIvvXUQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('0acda87e7e1ca62222c044dbcad7bd31')

# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        print(body, signature)
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 學你說話
@handler.add(MessageEvent, message=TextMessage)
def echo(event):
    
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        print(event)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text)
        )

if __name__ == "__main__":
    app.run()
