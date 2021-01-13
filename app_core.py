from __future__ import unicode_literals
import os
import configparser

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, PostbackEvent, LocationMessage, ImageMessage

import psycopg2
import datetime as dt
import flexmsg_g, flexmsg_r
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
    
#    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
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
            flexmsg_g.activity_type)

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
            flexmsg_r.activity_type_for_attendee
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
                            TextSendMessage(text = "請重新輸入")
                        )
                    
                    #如果還沒輸入到最後一格, 則繼續詢問下一題
                    postgres_select_query = f"""SELECT * FROM group_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                    cursor.execute(postgres_select_query)
                    data_g = cursor.fetchone()
                    print(f"輸入資料後 data_g:{data_g}")

                    if None in data_g:
                        i = data_g.index(None)
                        msg = flexmsg_g.flex(i, data_g, progress_target)
                        line_bot_api.reply_message(
                            event.reply_token,
                            msg)
                        print("問下一題")
                            
                    elif None not in data_g:

                        msg = flexmsg_g.summary(data_g)
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
                    # 在summary點選修改後
                    column = event.message.text
                     # 處理location 因為location 跟資料庫的名字不一樣
                    if column == "location":
                        postgres_update_query = f"""UPDATE group_data SET location_tittle = Null WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                        cursor.execute(postgres_update_query)
                        conn.commit()
                        progress_target=[7, 6, 6, 6, 6, 6, 6, 6]
                        msg = flexmsg_g.flex(column, data_g, progress_target)
                        line_bot_api.reply_message(
                            event.reply_token,
                            msg
                        )
                    elif column in column_all:
                        postgres_update_query = f"""UPDATE group_data SET {column} = Null WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                        cursor.execute(postgres_update_query)
                        conn.commit()
                        progress_target=[7, 6, 6, 6, 6, 6, 6, 6 ]
                        msg = flexmsg_g.flex(column, data_g, progress_target)
                        line_bot_api.reply_message(
                            event.reply_token,
                            msg
                        )
                    else :
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text= "請輸入想修改的欄位名稱")
                        )
                        
        elif data_r:
        
            if None in data_r:
                   
                i_r = data_r.index(None)
                record = event.message.text

                postgres_select_query = f"""SELECT activity_no FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                cursor.execute(postgres_select_query)
                activity_no = cursor.fetchone()[0] #取得正在報名的活動編號

                postgres_select_query = f"""SELECT phone FROM registration_data WHERE activity_no = '{activity_no}';"""
                cursor.execute(postgres_select_query)
                phone_registration = cursor.fetchall() #取得報名該團的電話列表
                        
                    #當進行到輸入電話時(i_r==4)，開始檢驗是否重複
                    if i_r == 4 and record in phone_registration[0]:
                        #如果使用者輸入的電話重複則報名失敗，刪掉原本創建的列
                        postgres_delete_query = f"""DELETE FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                        cursor.execute(postgres_delete_query)
                        conn.commit()

                        line_bot_api.reply_message(
                            event.reply_token,
                            [TextSendMessage(text = "不可重複報名 請重新選擇想要報名的活動類型"), flexmsg_r.activity_type_for_attendee]
                        )
                        #~~~這邊感覺可以設計一個flex_msg，出現[返回]按鈕，重新回到報名第一步(按鈕回傳~join)

                    else:
                        try:
                            # 輸入資料型態正確則更新
                            postgres_update_query = f"""UPDATE registration_data SET {column_all_registration[i_r]} = '{record}' WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                            cursor.execute(postgres_update_query)
                            conn.commit()
           
                        except:
                            # 輸入資料型態錯誤則回應 "請重新輸入"
                            line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(text = "請重新輸入")
                            )

                    # 檢查是否完成所有問題
                    postgres_select_query = f"""SELECT * FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                    cursor.execute(postgres_select_query)
                    data_r = cursor.fetchone() #準備寫入報名資料的那一列
                    print("i_r = ",i_r)
                    print("data_r = ",data_r)


                    if None in data_r:
                    
                        i_r = data_r.index(None)
                        msg = flexmsg.flex(i_r, progress_list_fullregistrationdata) #flexmsg需要新增報名情境
                        line_bot_api.reply_message(
                            event.reply_token,
                            msg
                        )
                    #出現summary
                    elif None not in data_r:
                        msg = flexmsg.summary_for_attend(data_r)
                        line_bot_api.reply_message(
                            event.reply_token,
                            msg
                        )
        
#處理postback 事件，例如datetime picker
@handler.add(PostbackEvent)
def gathering(event):
    progress_list_fullgroupdata=[7, 1, 2, 3, 4, 5, 6 ,7 ]
    progress_list_halfgroupdata=[5, 1, 2, 3, 4, 5]
    progress_target = progress_list_halfgroupdata
    progress_list_fullregistrationdata=[2, 0, 0, 0, 0, 0, 1, 2]

    activity_type = ['登山踏青', '桌遊麻將', '吃吃喝喝', '唱歌跳舞']
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
    
    # 按下rich menu中"我要報名" 選擇其中一種活動類型後
    elif postback_data in activity_type: #這裡的event.message.text會是上面quick reply回傳的訊息(四種type其中一種)

        DATABASE_URL = os.environ['DATABASE_URL']
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        postgres_select_query = f"""SELECT * FROM group_data WHERE activity_date >= '{dt.date.today()}' AND activity_type='{postback_data}'  and people > attendee and condition = 'pending' ORDER BY activity_date ASC ;"""
        cursor.execute(postgres_select_query)
        data_carousel = cursor.fetchall()

        msg = flexmsg_r.carousel(postback_data, data_carousel)
        line_bot_api.reply_message(
            event.reply_token,
            msg
        )

    elif "詳細資訊" in postback_data :
        record = postback_data.split("_")
        DATABASE_URL = os.environ['DATABASE_URL']
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        postgres_select_query = f"""SELECT * FROM group_data WHERE activity_no = '{record[0]}' ;"""
        cursor.execute(postgres_select_query)
        data_tmp = cursor.fetchone()
        msg = flexmsg_r.MoreInfoSummary(data_tmp)

        line_bot_api.reply_message(
            event.reply_token,
            msg
        )

    elif '立即報名' in postback_data: #點了"立即報名後即回傳activity_no和activity_name"
        record = postback_data.split("_")
        #record[0]:立即報名 record[1]：活動代號 record[2]:活動名稱

        #把只創建卻沒有寫入資料的列刪除
        postgres_delete_query = f"""DELETE FROM group_data WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
        cursor.execute(postgres_delete_query)
        conn.commit()
        postgres_delete_query = f"""DELETE FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
        cursor.execute(postgres_delete_query)
        conn.commit()

        #創建一列
        postgres_insert_query = f"""INSERT INTO registration_data (condition, user_id, activity_no, activity_name ) VALUES ('initial', '{event.source.user_id}','{record[1]}', '{record[2]}');"""
        cursor.execute(postgres_insert_query)
        conn.commit()

        #撈報團者的資料
        postgres_select_query=f'''SELECT attendee_name, phone FROM registration_data WHERE user_id = '{event.source.user_id}' AND condition != 'closed' ORDER BY record_no DESC;'''
        cursor.execute(postgres_select_query)
        data_for_basicinfo = cursor.fetchone()
        print("data_for_basicinfo = ",data_for_basicinfo)

        #審核電話
        postgres_select_query = f"""SELECT phone FROM registration_data WHERE activity_no = '{record[1]}' ;"""
        cursor.execute(postgres_select_query)
        phone_registration = cursor.fetchall()

        print(f"phone_registration:{phone_registration}")
            
        name = data_for_basicinfo[0]
        phone = data_for_basicinfo[1]
        
        if name != None and phone != None and phone not in phone_registration[0]:
            # 已有報名紀錄則直接帶入先前資料
            postgres_update_query = f"""UPDATE registration_data SET attendee_name='{data_for_basicinfo[0]}' , phone='{data_for_basicinfo[1]}' WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
            cursor.execute(postgres_update_query)
            conn.commit()
            postgres_select_query = f"""SELECT * FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
            cursor.execute(postgres_select_query)
            data_r = cursor.fetchone()
            msg = flexmsg_r.summary_for_attend(data_r)
            line_bot_api.reply_message(
                event.reply_token,
                msg
            )
    
        else:
            # 重新填寫報名資料
            postgres_select_query = f"""SELECT * FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
            cursor.execute(postgres_select_query)
            data_r = cursor.fetchone()
            i_r = data_r.index(None)
            print(f"count none in data_r = {data_r.count(None)}")
            print(f"i_r = {i_r}")
        
            msg = flexmsg_r.flex(i_r, progress_list_fullregistrationdata) #flexmsg需要新增報名情境
            line_bot_api.reply_message(
                event.reply_token,
                msg
            )

    
    else:
        # 開團時,填寫時間資料
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
            # 寫入資料(更新活動日期、時間，預填截止時間）
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
            i = data_g.index(None)
            msg = flexmsg_g.flex(i, data_g, progress_target)
            line_bot_api.reply_message(
                event.reply_token,
                msg)
        elif None not in data_g:
            msg = flexmsg_g.summary(data_g)
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
        i = data_g.index(None)
        msg = flexmsg_g.flex(i, data_g, progress_target)
        line_bot_api.reply_message(
            event.reply_token,
            msg)
    elif None not in data_g:
        msg=flexmsg_g.summary(data_g)
        line_bot_api.reply_message(
            event.reply_token,
            msg
        )
    cursor.close()
    conn.close()
    
'''
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
                    msg.append(flexmsg_g.summary(data_g))
                    
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
'''

if __name__ == "__main__":
    app.run()
