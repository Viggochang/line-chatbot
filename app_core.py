from __future__ import unicode_literals
import os
import configparser

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, PostbackEvent, LocationMessage, ImageMessage

import psycopg2
import datetime as dt
import flexmsg
import cancel

app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    print(body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 學你說話
@handler.add(MessageEvent, message=TextMessage)
def app_core(event):
    
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
#        line_bot_api.reply_message(
#        event.reply_token,
#        TextSendMessage(text=event.message.text)
#        )
        
        DATABASE_URL = os.environ['DATABASE_URL']
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        print("連接資料庫")

        if event.message.text == "~cancel":
            cancel.cancel(cursor, event)
#            postgres_select_query=f'''SELECT * FROM group_data WHERE user_id = '{event.source.user_id}' AND condition= 'initial';'''
#            cursor.execute(postgres_select_query)
#            data = cursor.fetchone()
#
#            postgres_select_query=f'''SELECT * FROM registration_data WHERE user_id = '{event.source.user_id}' AND condition= 'initial';'''
#            cursor.execute(postgres_select_query)
#            data_2 = cursor.fetchone()
#
#            postgres_delete_query = f"""DELETE FROM group_data WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
#            cursor.execute(postgres_delete_query)
#            conn.commit()
#            postgres_delete_query = f"""DELETE FROM registration_data WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
#            cursor.execute(postgres_delete_query)
#            conn.commit()
#
#            cursor.close()
#            conn.close()
#
#            if data or data_2:
#                line_bot_api.reply_message(
#                event.reply_token,
#                TextSendMessage(text='取消成功')
#                )
#            else:
#                line_bot_api.reply_message(
#                event.reply_token,
#                TextSendMessage(text='無可取消的開團/報名資料')
#                )


        elif event.message.text == "我要開團":
            line_bot_api.reply_message(
                event.reply_token,
                flexmsg.activity_type)

            print("準備開團")

            #把只創建卻沒有寫入資料的列刪除
            postgres_delete_query = f"""DELETE FROM group_data WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
            cursor.execute(postgres_delete_query)
            conn.commit()
            postgres_delete_query = f"""DELETE FROM registration_data WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
            cursor.execute(postgres_delete_query)
            conn.commit()

            #創建一列(condition = initial)
            postgres_insert_query = f"""INSERT INTO group_data (condition, user_id, attendee, photo, description) VALUES ('initial', '{event.source.user_id}', '1', '無', '無');"""
            cursor.execute(postgres_insert_query)
            conn.commit()
            #撈主揪的資料
            postgres_select_query=f'''SELECT name,phone FROM group_data WHERE user_id = '{event.source.user_id}' AND condition!= 'initial' ORDER BY activity_no DESC;'''
            cursor.execute(postgres_select_query)
            data_for_basicinfo = cursor.fetchone()

            if data_for_basicinfo:
                postgres_update_query = f"""UPDATE group_data SET name='{data_for_basicinfo[0]}' , phone='{data_for_basicinfo[1]}' WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
                cursor.execute(postgres_update_query)
                conn.commit()

            cursor.close()
            conn.close()
        
        

if __name__ == "__main__":
    app.run()
