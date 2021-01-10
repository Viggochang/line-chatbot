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
    
    print(f"body:{body}")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 學你說話
@handler.add(MessageEvent, message=TextMessage)
def app_core(event):
    progress_list_fullgroupdata=[7, 1, 2, 3, 4, 5, 6 ,7 ]
    progress_list_halfgroupdata=[5, 1, 2, 3, 4, 5]
    
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
#        line_bot_api.reply_message(
#        event.reply_token,
#        TextSendMessage(text=event.message.text)
#        )
        print(f"event:{event}")
        DATABASE_URL = os.environ['DATABASE_URL']
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        print("連接資料庫")

        if event.message.text == "~cancel":
            cancel.cancel(line_bot_api, cursor, conn, event)

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
            postgres_select_query=f'''SELECT name,phone FROM group_data WHERE user_id = '{event.source.user_id}' AND condition != 'initial' ORDER BY activity_no DESC;'''
            cursor.execute(postgres_select_query)
            data_for_basicinfo = cursor.fetchone()

            if data_for_basicinfo:
                postgres_update_query = f"""UPDATE group_data SET name='{data_for_basicinfo[0]}' , phone='{data_for_basicinfo[1]}' WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
                cursor.execute(postgres_update_query)
                conn.commit()

            cursor.close()
            conn.close()
            
        elif event.message.text == "我要報名":
            line_bot_api.reply_message(
                event.reply_token,
                flexmsg.activity_type
            )
            
            print("準備可報名團資訊")
            
            #把只創建卻沒有寫入資料的列刪除
            postgres_delete_query = f"""DELETE FROM group_data WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
            cursor.execute(postgres_delete_query)
            conn.commit()
            postgres_delete_query = f"""DELETE FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
            cursor.execute(postgres_delete_query)
            conn.commit()
            
        else:
            postgres_select_query = f"""SELECT * FROM group_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
            cursor.execute(postgres_select_query)
            data_g = cursor.fetchone()
            print(f"data_g:{data_g}")
            column_all = ['acrivity_no', 'activity_type', 'activity_name',
                          'activity_date', 'activity_time', 'location_tittle', 'lat', 'long', 'people', 'cost',
                          'due_date', 'description', 'photo', 'name',
                          'phone', 'mail', 'attendee', 'condition', 'user_id']
        
            postgres_select_query = f"""SELECT * FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
            cursor.execute(postgres_select_query)
            #準備寫入報名資料的那一列
            data_r = cursor.fetchone()
            print(f"data_r:{data_r}")
            column_all_registration = ['record_no', 'activity_no',
                                       'activity_name', 'attendee_name', 'phone',
                                       'mail', 'condition', 'user_id']
            
            activity_type = ['登山踏青', '桌遊麻將', '吃吃喝喝', '唱歌跳舞']
            
            if data_g:
                progress_target = progress_list_halfgroupdata
                
                if None in data_g:
                    i = data_g.index(None)
                    print(f"i={i}")
                    
                    if False:
                        pass
                    else:
                        record = event.message.text
                        #如果使用者輸入的資料不符合資料庫的資料型態, 則回覆 請重新輸入
                        try:
                            #輸入資料
                            postgres_update_query = f"""UPDATE group_data SET {column_all[i]} = '{record}' WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                            cursor.execute(postgres_update_query)
                            conn.commit()
                            
                        except:
                            line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(text="請重新輸入")
                            )
                        
                        #如果還沒輸入到最後一格, 則繼續詢問下一題
                        postgres_select_query = f"""SELECT * FROM group_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                        cursor.execute(postgres_select_query)
                        data_g = cursor.fetchone()
                        print(f"輸入資料後 data_g:{data_g}")

                        if None in data_g:
                            msg = flexmsg.flex(i, data_g, progress_target)
                            line_bot_api.reply_message(
                                event.reply_token,
                                msg)
                            print("問下一題")
                                
                        elif None not in data_g:

                            msg = flexmsg.summary(data_g)
                            line_bot_api.reply_message(
                                event.reply_token,
                                msg
                            )
                            
                else:
                    if event.message.text == '確認開團':

                        postgres_update_query = f"""UPDATE group_data SET condition = 'pending' WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                        cursor.execute(postgres_update_query)
                        conn.commit()

                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text = "開團成功！")
                        )

                        cursor.close()
                        conn.close()
                        
                    else:
                        column = event.message.text
                         # 處理location 因為location 跟資料庫的名字不一樣
                        if column == "location":
                            postgres_update_query = f"""UPDATE group_data SET location_tittle = Null WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                            cursor.execute(postgres_update_query)
                            conn.commit()
                            progress_target=[7, 6, 6, 6, 6, 6, 6, 6]
                            msg=flexmsg.flex(column, data_g, progress_target)
                            line_bot_api.reply_message(
                                event.reply_token,
                                msg
                            )
                        elif column in column_all:
                            postgres_update_query = f"""UPDATE group_data SET {column} = Null WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                            cursor.execute(postgres_update_query)
                            conn.commit()
                            progress_target=[7, 6, 6, 6, 6, 6, 6, 6 ]
                            msg = flexmsg.flex(column, data_g, progress_target)
                            line_bot_api.reply_message(
                                event.reply_token,
                                msg
                            )
                        else :
                            line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(text= "請輸入想修改的欄位名稱")
                            )

#處理postback 事件，例如datetime picker
@handler.add(PostbackEvent)
def gathering(event):
    progress_list_fullgroupdata=[7, 1, 2, 3, 4, 5, 6 ,7 ]
    progress_list_halfgroupdata=[5, 1, 2, 3, 4, 5]
    progress_target = progress_list_halfgroupdata

    print(f"postback_event:{event}")
                    
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    postgres_select_query = f"""SELECT * FROM group_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
    cursor.execute(postgres_select_query)
    data_g = cursor.fetchone()
    postback_data = event.postback.data
    
    if False:
        pass
        
    else:

        i = data_g.index(None)
        print("i =",i)
        column_all = ['acrivity_no', 'activity_type', 'activity_name',
                      'activity_date', 'activity_time', 'location_tittle', 'lat', 'long', 'people', 'cost',
                      'due_date', 'description', 'photo', 'name',
                      'phone', 'mail', 'attendee', 'condition', 'user_id']
        #處理activity date and time
        if event.postback.data == "Activity_time" :

            record = event.postback.params['datetime']
            record = record.split("T")
            print(record)
            temp = dt.datetime.strptime(record[0], "%Y-%m-%d") - dt.timedelta(days=1)
            # 寫入資料(更新活動時間)
            postgres_update_query = f"""UPDATE group_data SET ({column_all[i]},{column_all[i+1]},{column_all[i+7]} ) = ('{record[0]}','{record[1]}','{temp}') WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
            cursor.execute(postgres_update_query)
            conn.commit()

            #處理due date
        elif event.postback.data == "Due_time":

            record = event.postback.params['date']
            # 寫入資料(更新截止時間)
            postgres_update_query = f"""UPDATE group_data SET {column_all[i]} = '{record}' WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
            cursor.execute(postgres_update_query)
            conn.commit()

        #postgres_select_query = f"""SELECT * FROM group_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
        cursor.execute(postgres_select_query)
        data_g = cursor.fetchone()

        if None in data_g:
            msg = flexmsg.flex(i, data_g, progress_target)
            line_bot_api.reply_message(
                event.reply_token,
                msg)
        elif None not in data_g:
            msg = flexmsg.summary(data_g)
            line_bot_api.reply_message(
                event.reply_token,
                msg)
                
        cursor.close()
        conn.close()

@handler.add(MessageEvent, message=LocationMessage)
def gathering(event):
    progress_list_fullgroupdata=[7, 1, 2, 3, 4, 5, 6 ,7 ]
    progress_list_halfgroupdata=[5, 1, 2, 3, 4, 5]
    progress_target = progress_list_halfgroupdata
    
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    postgres_select_query = f"""SELECT * FROM group_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
    cursor.execute(postgres_select_query)
    data_g = cursor.fetchone()
    
    i = data_g.index(None)
    print("i =",i)
    column_all = ['acrivity_no', 'activity_type', 'activity_name',
                  'activity_date', 'activity_time', 'location_tittle', 'lat', 'long', 'people', 'cost',
                  'due_date', 'description', 'photo', 'name',
                  'phone', 'mail', 'attendee', 'condition', 'user_id']

    record = [event.message.title, event.message.latitude, event.message.longitude]
    if record[0] == None:
        record[0] = event.message.address[:50]
    # 寫入資料(更新位置資訊)
    postgres_update_query = f"""UPDATE group_data SET ({column_all[i]}, {column_all[i+1]}, {column_all[i+2]}) = ('{record[0]}', '{record[1]}', '{record[2]}') WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
    cursor.execute(postgres_update_query)
    conn.commit()
    
    cursor.execute(postgres_select_query)
    data_g = cursor.fetchone()
    
    if None in data_g:
        msg = flexmsg.flex(i, data_g, progress_target)
        line_bot_api.reply_message(
            event.reply_token,
            msg)
    elif None not in data_g:
        msg=flexmsg.summary(data_g)
        line_bot_api.reply_message(
            event.reply_token,
            msg
        )
    cursor.close()
    conn.close()
    
    
@handler.add(MessageEvent, message=ImageMessage)
def pic(event):
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    postgres_select_query = f"""SELECT * FROM group_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
    cursor.execute(postgres_select_query)
    data_g = cursor.fetchone()
    if data_g:
        i = data_g.index(None)
        print("i =",i)
        if i == 12:
            column_all = ['acrivity_no', 'activity_type', 'activity_name',
                          'activity_date', 'activity_time', 'location_tittle', 'lat', 'long', 'people', 'cost',
                          'due_date', 'description', 'photo', 'name',
                          'phone', 'mail', 'attendee', 'condition', 'user_id']
            #把圖片存下來並傳上去
            ext = 'jpg'
            message_content = line_bot_api.get_message_content(event.message.id)
            with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
                for chunk in message_content.iter_content():
                    tf.write(chunk)
                tempfile_path = tf.name

            dist_path = tempfile_path + '.' + ext
            dist_name = os.path.basename(dist_path)
            os.rename(tempfile_path, dist_path)

            try:
                config = configparser.ConfigParser()
                config.read('config.ini')
                client = ImgurClient(config.get('imgur', 'client_id'), config.get('imgur', 'client_secret'), config.get('imgur', 'access_token'), config.get('imgur', 'refresh_token'))
                con = {
                    'album': config.get('imgur', 'album_id'),
                    'name': f'{event.source.user_id}_{data_g[3]}',
                    'title': f'{event.source.user_id}_{data_g[3]}',
                    'description': f'{event.source.user_id}_{data_g[3]}'
                }
                path = os.path.join('static', 'tmp', dist_name)
                image=client.upload_from_path(path, config=con, anon=False)
                print("path = ",path)
                os.remove(path)
                print("image = ",image)
                #把圖片網址存進資料庫
                postgres_update_query = f"""UPDATE group_data SET {column_all[i]} = '{image['link']}' WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                cursor.execute(postgres_update_query)
                conn.commit()
                
                msg=[TextSendMessage(text='上傳成功'),
                     ImageSendMessage(original_content_url=image['link'], preview_image_url=image['link']),
                     TextSendMessage(text=request.host_url + os.path.join('static', 'tmp', dist_name)+"\n\n"+image['link'])]
                
                postgres_select_query = f"""SELECT * FROM group_data WHERE user_id = '{event.source.user_id}' ORDER BY activity_no DESC;"""
                cursor.execute(postgres_select_query)
                data_g = cursor.fetchone()
                
                if None not in data_g:
                    msg.append(flexmsg.summary(data_g))
                    
                    line_bot_api.reply_message(
                        event.reply_token,
                        msg
                    )
            except:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='上傳失敗'))

    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "現在不用傳圖片給我")
        )
    return 0


if __name__ == "__main__":
    app.run()
