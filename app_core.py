# 載入需要的模組
from __future__ import unicode_literals
from imgurpython import ImgurClient
import os, tempfile
import psycopg2
import datetime as dt
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, PostbackEvent, LocationMessage, ImageMessage
import configparser
import flexmsg

app = Flask(__name__)
#存圖片要用
static_tmp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'tmp')
# # function for create tmp dir for download content
# def make_static_tmp_dir():
#     try:
#         os.makedirs(static_tmp_path)
#     except OSError as exc:
#         if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
#             pass
#         else:
#             raise
# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

#check upload
@app.route("/")
def hello():
    return "Hello, world!"

# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text = True)
    app.logger.info("Request body: " + body)

    print(body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 學你說話
@handler.add(MessageEvent, message = TextMessage)
def echo(event):
    # [0] 總題數 [1:]目前題數 
    progress_list_fullgroupdata = [7, 1, 2, 3, 4, 5, 6 ,7 ]
    progress_list_halfgroupdata = [5, 1, 2, 3, 4, 5]
    progress_list_fullregistrationdata = [2, 0, 0, 0, 0, 0, 1, 2]
    event.message.text = event.message.text.replace("'","‘")
    #progress_target
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        #連結到heroku資料庫
        DATABASE_URL = os.environ['DATABASE_URL']
        conn = psycopg2.connect(DATABASE_URL, sslmode = 'require')
        cursor = conn.cursor()

        
        if event.message.text == "我要開團":
            line_bot_api.reply_message(
                event.reply_token,
                flexmsg.activity_type)

            print("prepare to open the group")

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
            postgres_select_query = f'''SELECT name,phone FROM group_data WHERE user_id = '{event.source.user_id}' AND condition != 'initial' ORDER BY activity_no DESC;'''
            cursor.execute(postgres_select_query)
            data_for_basicinfo = cursor.fetchone()

            if data_for_basicinfo:
                postgres_update_query = f"""UPDATE group_data SET name = '{data_for_basicinfo[0]}' , phone = '{data_for_basicinfo[1]}' WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
                cursor.execute(postgres_update_query)
                conn.commit()

            cursor.close()
            conn.close()

        #中途想結束輸入~delete, 把initial那列刪除
        elif event.message.text == "取消" :
            postgres_select_query = f'''SELECT * FROM group_data WHERE user_id = '{event.source.user_id}' AND condition = 'initial';'''
            cursor.execute(postgres_select_query)
            data = cursor.fetchone()
            
            postgres_select_query = f'''SELECT * FROM registration_data WHERE user_id = '{event.source.user_id}' AND condition = 'initial';'''
            cursor.execute(postgres_select_query)
            data_2 = cursor.fetchone()

            postgres_delete_query = f"""DELETE FROM group_data WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
            cursor.execute(postgres_delete_query)
            conn.commit()
            postgres_delete_query = f"""DELETE FROM registration_data WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
            cursor.execute(postgres_delete_query)
            conn.commit()
            
            
            if data or data_2:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = '取消成功')
                )
            else:
                    line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = '無可取消的開團/報名資料')
                )
        
        elif event.message.text == "我要報名":
            #把只創建卻沒有寫入資料的列刪除
            postgres_delete_query = f"""DELETE FROM group_data WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
            cursor.execute(postgres_delete_query)
            conn.commit()
            postgres_delete_query = f"""DELETE FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
            cursor.execute(postgres_delete_query)
            conn.commit()
            msg = flexmsg.activity_type_for_attendee
            line_bot_api.reply_message(
                event.reply_token,
                msg
            )


        
        #如果有創建了一列, 則接下來的資料繼續寫入
        else:
            postgres_select_query = f"""SELECT * FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
            cursor.execute(postgres_select_query)
            #準備寫入報名資料的那一列
            data_2 = cursor.fetchone() 
            print("data_2 :",data_2)
            column_all_registration = ['record_no', 'activity_no', 
                                       'activity_name', 'attendee_name', 'phone', 
                                       'mail', 'condition', 'user_id']
            
            activity_type = ['登山踏青', '桌遊麻將', '吃吃喝喝', '唱歌跳舞']
            
            postgres_select_query = f"""SELECT * FROM group_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
            cursor.execute(postgres_select_query)
            data = cursor.fetchone()
            print('data = ', data)
            column_all = ['acrivity_no', 'activity_type', 'activity_name', 
                          'activity_date', 'activity_time', 'location_tittle', 'lat', 'long', 'people', 'cost', 
                          'due_date', 'description', 'photo', 'name', 
                          'phone', 'mail', 'attendee', 'condition', 'user_id']

            if data:
                try:
                    if len(data[14])>0:
                        progress_target = progress_list_halfgroupdata
                    else :
                        progress_target = progress_list_fullgroupdata
                except:
                    progress_target = progress_list_fullgroupdata
                    
                if None in data:
                    i = data.index(None)
                    print("i = ",i)
                    if i == 5:
                        line_bot_api.reply_message(
                            event.reply_token,
                            [TextSendMessage(text = "請點選按鈕選擇活動地點，謝謝。"),flexmsg.location(progress_target)]
                        )
                    elif i==12:
                        postgres_update_query = f"""UPDATE group_data SET {column_all[i]} = '無' WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                        cursor.execute(postgres_update_query)
                        conn.commit()
                        postgres_select_query = f"""SELECT * FROM group_data WHERE user_id = '{event.source.user_id}' ORDER BY activity_no DESC;"""
                        cursor.execute(postgres_select_query)
                        data = cursor.fetchone()
                        msg=flexmsg.summary(data)
                        line_bot_api.reply_message(
                            event.reply_token,
                            [TextSendMessage(text = "上傳失敗。"), msg]
                        )

                    else:
                        record = event.message.text
                        #如果使用者輸入的資料不符合資料庫的資料型態, 則輸入N/A
                        try:
                            postgres_update_query = f"""UPDATE group_data SET {column_all[i]} = '{record}' WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                            cursor.execute(postgres_update_query)
                            conn.commit()
                        except:
                            line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(text = "請重新輸入")
                            )

                       #如果還沒輸入到最後一格, 則繼續詢問下一題
                        postgres_select_query = f"""SELECT * FROM group_data WHERE condition = 'initial'AND user_id = '{event.source.user_id}';"""
                        cursor.execute(postgres_select_query)
                        data = cursor.fetchone()

                        if None in data: 
                            msg = flexmsg.flex(i, data, progress_target)
                            line_bot_api.reply_message(
                                event.reply_token,
                                msg)

                        #如果已經到最後一格, condition改為finish, 回覆summary，
                        elif None not in data:

                            postgres_select_query = f"""SELECT * FROM group_data WHERE user_id = '{event.source.user_id}' ORDER BY activity_no DESC;"""
                            cursor.execute(postgres_select_query)
                            data = cursor.fetchone()
                            msg = flexmsg.summary(data)
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
                            TextSendMessage(text = "開團成功")
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
                            progress_target = [7, 6, 6, 6, 6, 6, 6, 6 ]
                            msg = flexmsg.flex(column, data, progress_target)
                            line_bot_api.reply_message(
                                event.reply_token,
                                msg
                            )
                        elif column in column_all:
                            postgres_update_query = f"""UPDATE group_data SET {column} = Null WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                            cursor.execute(postgres_update_query)
                            conn.commit()
                            progress_target = [7, 6, 6, 6, 6, 6, 6, 6 ]
                            msg = flexmsg.flex(column, data, progress_target)
                            line_bot_api.reply_message(
                                event.reply_token,
                                msg
                            )
                        else :
                            line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(text = '請輸入您想修改的欄位')
                            )
                            
            elif event.message.text in activity_type: #這裡的event.message.text會是上面quick reply回傳的訊息(四種type其中一種)        
                DATABASE_URL = os.environ['DATABASE_URL']
                conn = psycopg2.connect(DATABASE_URL, sslmode = 'require')
                cursor = conn.cursor()
                postgres_select_query = f"""SELECT * FROM group_data WHERE activity_date >= '{dt.date.today()}' AND due_date >= '{dt.date.today()}' AND activity_type='{event.message.text}'  and people > attendee and condition = 'pending' ORDER BY activity_date ASC ;"""
                cursor.execute(postgres_select_query)
                data_2 = cursor.fetchall()
                msg = flexmsg.carousel(data_2)
                line_bot_api.reply_message(
                    event.reply_token,
                    msg
                )
            elif '其他類型' in event.message.text: #這裡的event.message.text是上面quick reply回傳的訊息(不是四種type)        
                DATABASE_URL = os.environ['DATABASE_URL']
                conn = psycopg2.connect(DATABASE_URL, sslmode = 'require')
                cursor = conn.cursor()
                postgres_select_query = f"""SELECT * FROM group_data WHERE activity_date >= '{dt.date.today()}' AND due_date >= '{dt.date.today()}' AND activity_type != '登山踏青' AND activity_type != '桌遊麻將' AND activity_type != '吃吃喝喝' AND activity_type !=  '唱歌跳舞'  and people > attendee and condition = 'pending' ORDER BY activity_date ASC ;"""
                cursor.execute(postgres_select_query)
                data_2 = cursor.fetchall()
                msg = flexmsg.carousel(data_2)
                line_bot_api.reply_message(
                    event.reply_token,
                    msg
                )

            



            elif data_2:
                if None in data_2:
                   
                    i_2 = data_2.index(None)

                    record = event.message.text

                    #當進行到輸入電話時(i_2 == 4)，開始檢驗是否重複
                    if i_2 == 4:
                        postgres_select_query = f"""SELECT activity_no FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                        cursor.execute(postgres_select_query)
                        activity_no = cursor.fetchone()[0] 

                        postgres_select_query = f"""SELECT phone FROM registration_data WHERE activity_no = '{activity_no}';"""
                        cursor.execute(postgres_select_query)
                        phone_registration = cursor.fetchall()

                        #如果使用者輸入的電話重複則報名失敗，刪掉原本創建的列

                        if (f'{record}',) in phone_registration:
                            postgres_delete_query = f"""DELETE FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                            cursor.execute(postgres_delete_query)
                            conn.commit()

                            line_bot_api.reply_message(
                                event.reply_token,
                                [TextSendMessage(text = "不可重複報名"), flexmsg.activity_type]
                            )
                            #~~~這邊感覺可以設計一個flex_msg，出現[返回]按鈕，重新回到報名第一步(按鈕回傳~join)

                        else:
                            postgres_update_query = f"""UPDATE registration_data SET {column_all_registration[i_2]} = '{record}' WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                            cursor.execute(postgres_update_query)
                            conn.commit()
           

                    else:    
                        #如果使用者輸入的資料不符合資料庫的資料型態, 則輸入N/A
                        try:
                            postgres_update_query = f"""UPDATE registration_data SET {column_all_registration[i_2]} = '{record}' WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                            cursor.execute(postgres_update_query)
                            conn.commit()
                        except:
                            line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(text = "請重新輸入")
                            )

                    postgres_select_query = f"""SELECT * FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                    cursor.execute(postgres_select_query)
                    data_2 = cursor.fetchone() #準備寫入報名資料的那一列  
                    print("i_2 = ",i_2)
                    print("data_2 = ",data_2)


                    if None in data_2:
                        msg_2 = flexmsg.extend(i_2 + 1, data_2, progress_list_fullregistrationdata) #flexmsg需要新增報名情境
                        line_bot_api.reply_message(
                            event.reply_token,
                            msg_2
                        )               
                    #出現summary
                    elif None not in data_2:
                        msg_2 = flexmsg.summary_for_attend(data_2)
                        line_bot_api.reply_message(
                            event.reply_token,
                            msg_2
                        )

                else:
                    if event.message.text == '確認報名':
                        #找到他報的團的編號activity_no
                        postgres_select_query = f"""SELECT activity_no FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                        cursor.execute(postgres_select_query)
                        activity_no = cursor.fetchone()[0]

                        #找報該團現在的報名人數attendee並更新(+1)
                        postgres_select_query = f"""SELECT attendee, condition FROM group_data WHERE activity_no = {activity_no};"""
                        cursor.execute(postgres_select_query)
                        temp=cursor.fetchone()
                        attendee = temp[0]
                        condition = temp[1]
                        if condition == "closed":
                            line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(text = "報名失敗")
                            )
                        else:
                            attendee += 1 

                        #將更新的報名人數attendee記錄到報名表單group_data裡
                        postgres_update_query = f"""UPDATE group_data SET attendee = {attendee} WHERE activity_no = {activity_no};"""
                        cursor.execute(postgres_update_query)
                        conn.commit()

                        #檢查報名人數attendee是否達上限people
                        postgres_select_query = f"""SELECT people FROM group_data WHERE activity_no = {activity_no};"""
                        cursor.execute(postgres_select_query)
                        people = cursor.fetchone()[0]

                        if attendee == people:
                            postgres_update_query = f"""UPDATE group_data SET condition = 'closed' WHERE activity_no = {activity_no};"""
                            cursor.execute(postgres_update_query)
                            conn.commit()


                        #將報名表單的condition改成closed
                        postgres_update_query = f"""UPDATE registration_data SET condition = 'closed' WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                        cursor.execute(postgres_update_query)
                        conn.commit()

                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text = "報名成功")
                        )

                        cursor.close()
                        conn.close()
                    elif event.message.text in column_all_registration:
                        postgres_update_query = f"""UPDATE registration_data SET {event.message.text} = Null WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                        cursor.execute(postgres_update_query)
                        conn.commit()
                        msg_2 = flexmsg.extend(event.message.text, data_2, progress_list_fullregistrationdata) #flexmsg需要新增報名情境
                        line_bot_api.reply_message(
                            event.reply_token,
                            msg_2
                        ) 
                    else:
                        line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(text = '請輸入您想修改的欄位')
                            )
            
            
            else:

                if event.message.text.encode == "double":
                    line_bot_api.reply_message(
                        event.reply_token,
                        flexmsg.summary(data)
                    )

                elif event.message.text == "早安":
                    img = 'https://pic.pimg.tw/ellenlee0409/1566550498-3560465550.jpg'
                    line_bot_api.reply_message(
                        event.reply_token,
                        ImageSendMessage(original_content_url = img, preview_image_url = img)
                    )
            
#                 else:    
#                     line_bot_api.reply_message(
#                         event.reply_token,
#                         TextSendMessage(text = event.message.text)
#                     )
#處理postback 事件，例如datetime picker
@handler.add(PostbackEvent)
def gathering(event):
    progress_list_fullgroupdata = [7, 1, 2, 3, 4, 5, 6 ,7 ]
    progress_list_halfgroupdata = [5, 1, 2, 3, 4, 5]
    progress_list_fullregistrationdata = [2, 0, 0, 0, 0, 0, 1, 2]
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode = 'require')
    cursor = conn.cursor()
    postgres_select_query = f"""SELECT * FROM group_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
    cursor.execute(postgres_select_query)
    data = cursor.fetchone()
    postback_data = event.postback.data
    try:
        if len(data[14])>0:
            progress_target = progress_list_halfgroupdata
        else :
            progress_target = progress_list_fullgroupdata
    except:
        progress_target = progress_list_fullgroupdata
        #主揪查看自己開的團的資訊 (活動名稱、地點、時間、費用、已報名人數)
    if "我的開團" in postback_data:
        #把只創建卻沒有寫入資料完成的列刪除
        postgres_delete_query = f"""DELETE FROM group_data WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
        cursor.execute(postgres_delete_query)
        conn.commit()
        postgres_delete_query = f"""DELETE FROM registration_data WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
        cursor.execute(postgres_delete_query)
        conn.commit()
        
        postgres_select_query = f"""SELECT * FROM group_data WHERE user_id = '{event.source.user_id}' AND activity_date >= '{dt.date.today()}' ORDER BY activity_date ASC;"""
        cursor.execute(postgres_select_query)
        group_data = cursor.fetchall()

        print("group_data = ", group_data)

        msg = flexmsg.GroupLst(group_data)
        line_bot_api.reply_message(
            event.reply_token,
            msg
            )
    elif "我的報名" in postback_data:
        #把只創建卻沒有寫入資料完成的列刪除
        postgres_delete_query = f"""DELETE FROM group_data WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
        cursor.execute(postgres_delete_query)
        conn.commit()
        postgres_delete_query = f"""DELETE FROM registration_data WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
        cursor.execute(postgres_delete_query)
        conn.commit()
        
         #用user_id從database找出有報的團
        postgres_select_query = f"""SELECT * FROM registration_data WHERE user_id = '{event.source.user_id}'AND activity_date >= '{dt.date.today()}' ORDER BY activity_date ASC;"""
        cursor.execute(postgres_select_query)


        #避免look_up_data_registration裡的actinity_name重複
        look_up_data_registration = []
        act_no = []
        alldata = cursor.fetchall()
        if alldata:
            for act in alldata: 
                if act[1] not in act_no:  #act[1]為activity_no, act[2]為activity_name
                    act_no.append(act[1])
                    look_up_data_registration.append(act)
                    print(act)

        msg = flexmsg.registration_list(look_up_data_registration)
        line_bot_api.reply_message(
            event.reply_token,
            msg
        )
    elif "開團資訊" in postback_data:
        activity_no = postback_data.replace("開團資訊", "")
        
        postgres_select_query = f"""SELECT * FROM group_data WHERE activity_no = '{activity_no}';"""
        cursor.execute(postgres_select_query)
        group_data = cursor.fetchone()

        print("group_data = ", group_data)

        msg = flexmsg.MyGroupInfo(group_data)
        line_bot_api.reply_message(
            event.reply_token,
            msg
            )
        
    #主揪查看報名者資訊(報名者暱稱、電話)
    elif "報名者資訊" in postback_data:
        activity_no = postback_data.replace("報名者資訊", "")

        postgres_select_query = f"""SELECT activity_name FROM registration_data WHERE activity_no = '{activity_no}';"""
        cursor.execute(postgres_select_query)

#         try:
        temp = cursor.fetchone()
        if temp:
            activity_name = "".join(temp)
            print("activity_name = ", activity_name)

            postgres_select_query = f"""SELECT attendee_name, phone FROM registration_data WHERE activity_no = '{activity_no}' ;"""
            cursor.execute(postgres_select_query)
            attendee_data = cursor.fetchall()
            print("attendee_data = ", attendee_data)

            attendee_lst = []
            for row in attendee_data:
                attendee_lst.append(" ".join(row))

            msg = f"{activity_name}"+"\n報名者資訊："
            for attendee in attendee_lst:
                msg += f"\n{attendee}"
    #         except:
    #             msg = "本活動目前無人報名"

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text = msg)
                )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text = '目前無人報名')
                )

    #主揪提早關團
    elif "結束報名" in postback_data:
        activity_no = postback_data.replace("結束報名", "")
        
        postgres_update_query = f"""UPDATE group_data SET condition = 'closed' WHERE activity_no = '{activity_no}';"""
        cursor.execute(postgres_update_query)
        conn.commit()

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "成功結束報名！")
            )
    elif "查報名" in postback_data: #點選列表裡的活動將回傳(activity_no_查報名)
        activity_no = postback_data.split('_')[0]

        #根據回傳的activity_no，從group_data裡找到活動資訊
        postgres_select_query = f"""SELECT * FROM group_data WHERE activity_no = {activity_no};"""
        cursor.execute(postgres_select_query)
        group_info = cursor.fetchone()
        #根據回傳的activity_no和user_id找到報名資訊(可能不只一列)
        postgres_select_query = f"""SELECT * FROM registration_data WHERE activity_no = {activity_no} AND user_id = '{event.source.user_id}';"""
        cursor.execute(postgres_select_query)
        registration_info = cursor.fetchall()

        msg = flexmsg.carousel_registration(group_info, registration_info)
        line_bot_api.reply_message(
            event.reply_token,
            msg
        )    
         # bubble的input為"group_info"和"registration_info"
         # 報名資訊要有"取消報名"按鈕

    elif "取消報名" in postback_data: #按下取消報名按鈕將回傳(record_activity_取消報名)
        record_no = postback_data.split('_')[0]
        activity_no = postback_data.split('_')[1]

        postgres_delete_query = f"""DELETE FROM registration_data WHERE record_no = {record_no} AND user_id = '{event.source.user_id}';"""
        cursor.execute(postgres_delete_query)
        conn.commit()

        #找報該團現在的報名人數attendee並更新(-1)
        postgres_select_query = f"""SELECT attendee FROM group_data WHERE activity_no = {activity_no};"""
        cursor.execute(postgres_select_query)
        attendee = cursor.fetchone()[0]
        attendee -= 1

        #將更新的報名人數attendent記錄到報名表單group_data裡
        postgres_update_query = f"""UPDATE group_data SET attendee = {attendee} WHERE activity_no = {activity_no};"""
        cursor.execute(postgres_update_query)
        conn.commit()

        #更新該活動的condition(= pending)
        postgres_update_query = f"""UPDATE group_data SET condition = 'pending' WHERE activity_no = {activity_no};"""
        cursor.execute(postgres_update_query)
        conn.commit()

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "取消成功!")
        )
    elif "詳細資訊" in postback_data :
        record=postback_data.split("_")
        DATABASE_URL = os.environ['DATABASE_URL']
        conn = psycopg2.connect(DATABASE_URL, sslmode = 'require')
        cursor = conn.cursor()
        postgres_select_query = f"""SELECT * FROM group_data WHERE activity_no = '{record[0]}' ;"""
        cursor.execute(postgres_select_query)
        data_tmp = cursor.fetchone()
        msg = flexmsg.MoreInfoSummary(data_tmp)

        line_bot_api.reply_message(
            event.reply_token,
            msg
        )
                
         #~~點了carousel的"了解更多"，跳出該團的summary

    elif '立即報名' in postback_data: #點了"立即報名後即回傳activity_no和activity_name"
        record = postback_data.split("_")
        #record[0]:立即報名 record[1]：活動代號 record[2]:活動名稱 record[3]: 活動日期

        #把只創建卻沒有寫入資料的列刪除
        postgres_delete_query = f"""DELETE FROM group_data WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
        cursor.execute(postgres_delete_query)
        conn.commit()
        postgres_delete_query = f"""DELETE FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
        cursor.execute(postgres_delete_query)
        conn.commit()

        #創建一列
        postgres_insert_query = f"""INSERT INTO registration_data (condition, user_id, activity_no, activity_name, activity_date ) VALUES ('initial', '{event.source.user_id}','{record[1]}', '{record[2]}', '{record[3]}');"""
        cursor.execute(postgres_insert_query)   
        conn.commit()

        #撈報團者的資料
        postgres_select_query=f'''SELECT attendee_name, phone FROM registration_data WHERE user_id = '{event.source.user_id}' AND condition != 'initial' ORDER BY record_no DESC;'''
        cursor.execute(postgres_select_query)
        data_for_basicinfo = cursor.fetchone()
        print(" 651 data_for_basicinfo = ", data_for_basicinfo)
        
        #審核電話
        postgres_select_query = f"""SELECT phone FROM registration_data WHERE activity_no = '{record[1]}' ;"""
        cursor.execute(postgres_select_query)
        phone_registration = cursor.fetchall()

        #如果使用者輸入的電話重複則報名失敗，刪掉原本創建的列
        if data_for_basicinfo:
            phone = data_for_basicinfo[1]

            if (f'{phone}',) in phone_registration:
                postgres_select_query = f"""SELECT * FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                cursor.execute(postgres_select_query)
                data_2 = cursor.fetchone()
                i_2 = data_2.index(None)
                print("617 count none in data_2 = ",data_2.count(None))
                print("618 i_2", i_2)
                msg_2 = flexmsg.extend(i_2, data_2, progress_list_fullregistrationdata) #flexmsg需要新增報名情境
                line_bot_api.reply_message(
                    event.reply_token,
                    msg_2
                )

            else:
                postgres_update_query = f"""UPDATE registration_data SET attendee_name = '{data_for_basicinfo[0]}' , phone = '{data_for_basicinfo[1]}' WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
                cursor.execute(postgres_update_query)
                conn.commit()
                postgres_select_query = f"""SELECT * FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                cursor.execute(postgres_select_query)
                data_2 = cursor.fetchone()
                msg_2 = flexmsg.summary_for_attend(data_2)
                line_bot_api.reply_message(
                    event.reply_token,
                    msg_2
                )
        else:
            postgres_select_query = f"""SELECT * FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
            cursor.execute(postgres_select_query)
            data_2 = cursor.fetchone()
            i_2 = data_2.index(None)
            print("617 count none in data_2 = ",data_2.count(None))
            print("618 i_2", i_2)
            msg_2 = flexmsg.extend(i_2,data_2,progress_list_fullregistrationdata) #flexmsg需要新增報名情境
            line_bot_api.reply_message(
                event.reply_token,
                msg_2
            )

    elif "forward" in postback_data or "backward" in postback_data:
        
        record = postback_data.split("_") #record[0] = forward, reocord[1] = command

        if record[1] == "activity":

            #record[2] = activity_type, record[3] = i
            i = int(record[3])
            
            postgres_select_query = f"""SELECT * FROM group_data WHERE activity_date >= '{dt.date.today()}' AND due_date >= '{dt.date.today()}' AND activity_type = '{record[2]}' and people > attendee and condition = 'pending' ORDER BY activity_date ASC;"""
            cursor.execute(postgres_select_query)
            data = cursor.fetchall()
            
            msg = flexmsg.carousel(data, i)
            line_bot_api.reply_message(
                event.reply_token,
                msg
                )
            
        elif record[1] == "group":
            
            #record[2] = i
            i = int(record[2])       
            #用user_id尋找該主揪所有的開團資料
            postgres_select_query = f"""SELECT * FROM group_data WHERE user_id = '{event.source.user_id}' AND activity_date >= '{dt.date.today()}' ORDER BY activity_date ASC;"""
            cursor.execute(postgres_select_query)
            group_data = cursor.fetchall()

            print("group_data = ", group_data)

            #回傳開團列表
            msg = flexmsg.GroupLst(group_data, i)
            line_bot_api.reply_message(
                event.reply_token,
                msg
            )

        elif record[1] == "registration":

            #record[2] = i
            i = int(record[2])
            
            #用user_id從database找出有報的團
            postgres_select_query = f"""SELECT * FROM registration_data WHERE user_id = '{event.source.user_id}' AND activity_date >= '{dt.date.today()}' ORDER BY activity_date ASC;"""
            cursor.execute(postgres_select_query)

            #避免look_up_data_registration裡的actinity_name重複
            look_up_data_registration = []
            act_no = []
            alldata = cursor.fetchall()
            if alldata:
                for act in alldata: 
                    if act[1] not in act_no:  #act[1]為activity_no, act[2]為activity_name
                        act_no.append(act[1])
                        look_up_data_registration.append(act)

            msg = flexmsg.registration_list(look_up_data_registration, i)
            line_bot_api.reply_message(
                event.reply_token,
                msg
            )
        
#上一頁下一頁要寫在這個else上面
    else:

        i = data.index(None)
        print("i = ",i)
        column_all = ['acrivity_no', 'activity_type', 'activity_name', 
                      'activity_date', 'activity_time', 'location_tittle', 'lat', 'long', 'people', 'cost', 
                      'due_date', 'description', 'photo', 'name', 
                      'phone', 'mail', 'attendee', 'condition', 'user_id']
        #處理activity date and time
        if event.postback.data == "Activity_time" :

            record = event.postback.params['datetime']
            record = record.split("T")
            temp = dt.datetime.strptime(record[0], "%Y-%m-%d") - dt.timedelta(days = 1)
            postgres_update_query = f"""UPDATE group_data SET ({column_all[i]}, {column_all[i+1]}, {column_all[i+7]}) = ('{record[0]}', '{record[1]}', '{temp}') WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
            cursor.execute(postgres_update_query)
            conn.commit()

            #處理due date
        elif event.postback.data == "Due_time":

            record = event.postback.params['date']
            postgres_update_query = f"""UPDATE group_data SET {column_all[i]} = '{record}' WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
            cursor.execute(postgres_update_query)
            conn.commit()

        cursor.execute(postgres_select_query)
        data = cursor.fetchone()

        if None in data:
            msg=flexmsg.flex(i,data,progress_target)
            line_bot_api.reply_message(
                event.reply_token,
                msg)
        elif None not in data:
            postgres_select_query = f"""SELECT * FROM group_data WHERE user_id = '{event.source.user_id}' ORDER BY activity_no DESC;"""
            cursor.execute(postgres_select_query)
            data = cursor.fetchone()
            msg = flexmsg.summary(data)
            line_bot_api.reply_message(
                event.reply_token,
                msg
            )
        cursor.close()
        conn.close()

# location 事件
@handler.add(MessageEvent, message = LocationMessage)
def gathering(event):
    progress_list_fullgroupdata = [7, 1, 2, 3, 4, 5, 6 ,7 ]
    progress_list_halfgroupdata = [5, 1, 2, 3, 4, 5]
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    postgres_select_query = f"""SELECT * FROM group_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
    cursor.execute(postgres_select_query)
    data = cursor.fetchone()
    i = data.index(None)
    print("i =",i)
    column_all = ['acrivity_no', 'activity_type', 'activity_name', 
                  'activity_date', 'activity_time', 'location_tittle', 'lat', 'long', 'people', 'cost', 
                  'due_date', 'description', 'photo', 'name', 
                  'phone', 'mail', 'attendee', 'condition', 'user_id']
    tittle = event.message.title
    if event.message.title:
        tittle=event.message.title.replace("'","‘")
    record =[ tittle, event.message.latitude, event.message.longitude]
    if record[0] == None:
        record[0] = event.message.address[:50]
    postgres_update_query = f"""UPDATE group_data SET ({column_all[i]}, {column_all[i+1]}, {column_all[i+2]}) = ('{record[0]}', '{record[1]}', '{record[2]}') WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
    cursor.execute(postgres_update_query)
    conn.commit()
    cursor.execute(postgres_select_query)
    data = cursor.fetchone()
    try:
        if len(data[14])>0:
            progress_target = progress_list_halfgroupdata
        else :
            progress_target = progress_list_fullgroupdata
    except:
        progress_target = progress_list_fullgroupdata
    if None in data:
        msg = flexmsg.flex(i, data, progress_target)
        line_bot_api.reply_message(
            event.reply_token,
            msg)
    elif None not in data:
        postgres_select_query = f"""SELECT * FROM group_data WHERE user_id = '{event.source.user_id}' ORDER BY activity_no DESC;"""
        cursor.execute(postgres_select_query)
        data = cursor.fetchone()
        msg = flexmsg.summary(data)
        line_bot_api.reply_message(
            event.reply_token,
            msg
        )
    cursor.close()
    conn.close()
    
@handler.add(MessageEvent, message=ImageMessage)
def pic(event):
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode = 'require')
    cursor = conn.cursor()
    postgres_select_query = f"""SELECT * FROM group_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
    cursor.execute(postgres_select_query)
    data = cursor.fetchone()
    if data:
        i = data.index(None)
        print("i =",i)
        if i == 12:
            column_all = ['acrivity_no', 'activity_type', 'activity_name', 
                          'activity_date', 'activity_time', 'location_tittle', 'lat', 'long', 'people', 'cost', 
                          'due_date', 'description', 'photo', 'name', 
                          'phone', 'mail', 'attendee', 'condition', 'user_id']
            #把圖片存下來並傳上去
            ext = 'jpg'
            message_content = line_bot_api.get_message_content(event.message.id)
            with tempfile.NamedTemporaryFile(dir = static_tmp_path, prefix = ext + '-', delete = False) as tf:
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
                    'name': f'{event.source.user_id}_{data[3]}',
                    'title': f'{event.source.user_id}_{data[3]}',
                    'description': f'{event.source.user_id}_{data[3]}'
                }
                path = os.path.join('static', 'tmp', dist_name)
                image = client.upload_from_path(path, config = con, anon = False)
                print("path = ",path)
                os.remove(path)
                print("image = ",image)
                #把圖片網址存進資料庫
                postgres_update_query = f"""UPDATE group_data SET {column_all[i]} = '{image['link']}' WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                cursor.execute(postgres_update_query)
                conn.commit()
                
                msg = [TextSendMessage(text='上傳成功')]
                
                postgres_select_query = f"""SELECT * FROM group_data WHERE user_id = '{event.source.user_id}' ORDER BY activity_no DESC;"""
                cursor.execute(postgres_select_query)
                data = cursor.fetchone()
                if None not in data:
                    msg.append(flexmsg.summary(data))
                    
                line_bot_api.reply_message(
                    event.reply_token,
                    msg
                )
            except:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = '上傳失敗'))

    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "現在不用傳圖片給我")
        )
    return 0
@app.route('/static/<path:path>')
def send_static_content(path):
    return send_from_directory('static', path)

    
if __name__ == "__main__":
    app.run()
    # create tmp dir for download content
    #make_static_tmp_dir()
