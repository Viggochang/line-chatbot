from __future__ import unicode_literals
import os
import configparser
import psycopg2
import datetime as dt
import tempfile
import requests
from imgurpython import ImgurClient
from werkzeug.utils import secure_filename

from flask import Flask, request, abort, render_template, url_for, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
# from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, PostbackEvent, LocationMessage, ImageMessage

import flexmsg_g, flexmsg_r, flexmsg_glist, flexmsg_rlist, flexmsg_climate
import cancel
from custom_models import CallDatabase

app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()
print("連接資料庫")
    
# 網頁登錄
app.secret_key = config.get('flask', 'secret_key')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "請先登入後再使用喔！"

# 獲取所有會員資訊
users = CallDatabase.get_users()

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

class User(UserMixin):
    pass
    
@login_manager.user_loader # 確認是否在登入狀態
def user_loader(account):
    users = CallDatabase.get_users()
    print(f"user_loader: {users}")
    
    if account in users:
        user = User()
        user.id = account
        return user
  
@login_manager.request_loader
def request_loader(request):
    users = CallDatabase.get_users()
    print(f"request_loader: {users}")
    
    account = request.form.get("user_id")
    if account in users:
        user = User()
        user.id = account
        User.is_authenticated = request.form["password"] == users[account]["password"]
        return user

        
@app.route("/login", methods=['GET','POST'])
def login():
    # 獲取所有會員資訊
    users = CallDatabase.get_users()
    
    if request.method == 'GET':
        return render_template("login.html")
        
    else:  # request.method == 'POST'
        account = request.form["user_id"]
        if (account in users) and (request.form["password"] == users[account]["password"]):
            user = User()
            user.id = account
            login_user(user)
            print("登入成功")
            return render_template("home.html")  #回到首頁

        else:
            print("登入失敗")
            return render_template("login.html")
            
@app.route("/logout")
def logout():
    account = current_user.get_id()
    logout_user()
    print("登出成功")
    return redirect(url_for("login"))
    
@app.route("/new_account", methods=['GET','POST'])
def new_account():
    if request.method == 'GET':
        return render_template("new_account.html")
    else:
        user_name, user_phone, user_id, password = request.form["user_name"], request.form["user_phone"], request.form["user_id"], request.form["password"]
        
        columns = ("user_id", "password", "user_name", "user_phone")
        values = (user_id, password, user_name, user_phone)
        CallDatabase.insert("login", columns = columns, values = values)
        
        return render_template("login.html")
            
# flask 網頁
@app.route("/")
def home():
    return render_template("home.html")
    
@app.route("/more_information")
def more_information():
    return render_template("more_information.html")
    
@app.route("/from_start")
def from_start():
    return render_template("from_start.html")

# 我要開團
@app.route("/group", methods=['GET', 'POST'])
@login_required
def group():
    users = CallDatabase.get_users()
    print(f"group: {users}")
    if request.method == 'POST':
        
        
        columns = ("condition", "user_id", "attendee", "photo", "description")
        values = ("initial", current_user.get_id(), 1, "無", "無")
        CallDatabase.insert("group_data", columns = columns, values = values)
        
        columns, values = ["condition"], ["pending"]
        for g_col in request.form:
            if request.form[g_col]:
                value = request.form[g_col]
            # due_date 預設為活動前一天
            elif g_col == "due_date" and request.form[g_col] == "":
                activity_date = dt.datetime.strptime(request.form["activity_date"], '%Y-%m-%d')
                value = activity_date - dt.timedelta(days=1)
            
            columns.append(g_col)
            values.append(value)
                
        photo = request.files["photo"]
        if photo:
            filename = secure_filename(photo.filename)

            #把圖片存下來並傳上去
            file_path = f"/tmp/{filename}"
            with open(file_path, "wb") as tf:
                for chunk in photo:
                    tf.write(chunk)
                tempfile_path = tf.name

            dist_path = tempfile_path
            dist_name = os.path.basename(dist_path)
            print(f"dist_path={dist_path}", "\n", f"dist_name={dist_name}")

            try:
                config = configparser.ConfigParser()
                config.read('config.ini')
                client = ImgurClient(config.get('imgur', 'client_id'), config.get('imgur', 'client_secret'), config.get('imgur', 'access_token'), config.get('imgur', 'refresh_token'))
                con = {
                    'album': config.get('imgur', 'album_id'),
                    'name': f'{current_user}_{filename}',
                    'title': f'{current_user}_{filename}',
                    'description': f'{current_user}_{filename}'
                }

                image = client.upload_from_path(dist_path, config = con, anon = False)
                os.remove(dist_path)
                print("上傳成功")
                photo = image['link']
                
                columns.append("photo")
                values.append(photo)

            except:
                print("上傳失敗")
       
        condition = {"condition":["=", "initial"], "user_id":["=", current_user.get_id()]}
        CallDatabase.update("group_data", columns = columns, values = values, condition = condition)
        
        condition = {"condition":["=", "pending"], "user_id":["=", current_user.get_id()]}
        order = "activity_no"
        data_g = CallDatabase.get_data("group_data", condition, order, ASC = False, all_data = False)
        print(data_g)
        
        return render_template("group_summary.html", html_data = data_g)
        
    else:
        user_name = users[current_user.id]['user_name']
        user_phone = users[current_user.id]['user_phone']
        return render_template("group.html", html_data = [user_name, user_phone])
        
@app.route("/group_cancel", methods=['POST'])
def group_cancel(): #取消開團
    print(request.form)
    
    condition = {"activity_no": ["=", request.form['activity_no_cancel']]}
    CallDatabase.delete("group_data", condition = condition)
    
    return render_template("group_cancel.html")
    
@app.route("/group_closed", methods=['POST'])
def group_closed():
    activity_no = request.form["activity_no"]
    activity_name = request.form["activity_name"]
    print(activity_no, activity_name)
    #提早關團 condition >> closed by owner
    CallDatabase.update("group_data", columns = ["condition"], values = ["closed by owner"], condition = {"activity_no":["=", activity_no]})
    
    return render_template("group_closed.html", html_data = activity_name)

# 我要報名
@app.route("/registration", methods=['GET', 'POST'])
def registration():
    today_tw = (dt.datetime.now() + dt.timedelta(hours = 8)).date()
    condition = {"condition":["=", "pending"], "due_date":[">=", today_tw]}
    order = "activity_date"
    
    if request.method == 'POST':
        print(request.form)
        if request.form.get("activity_type", None):
            condition["activity_type"] = ["=", request.form["activity_type"]]
        if request.form.get("cost_min", None):
            condition["cost"] = [">=", request.form["cost_min"]]
        if request.form.get("cost_max", None):
            condition["cost"] = ["<=", request.form["cost_max"]]
            
        filter_data = CallDatabase.get_data("group_data", condition, order, ASC = True, all_data = True)
        filter_data = [filter_data[i: i+4] for i in range(len(filter_data)) if i%4 == 0]
        return render_template("registration.html", html_data = filter_data)
        
    else:
        all_groupdata = CallDatabase.get_data("group_data", condition, order, ASC = True, all_data = True)
        all_groupdata = [all_groupdata[i: i+4] for i in range(len(all_groupdata)) if i%4 == 0]
        return render_template("registration.html", html_data = all_groupdata)
        
@app.route("/r_detail", methods=['POST'])
@login_required
def r_detail(): # 詳細資料
    activity_no = request.form["activity_no"]
    condition = {"activity_no": ["=", activity_no]}
    
    data = CallDatabase.get_data("group_data", condition = condition, all_data = False)
    return render_template("r_detail.html", html_data = data)
    
@app.route("/r_summary", methods=['POST'])
@login_required
def r_summary():
    users = CallDatabase.get_users()
    print(f"registration: {users}")
    
    print(request.form)
    user_name = users[current_user.id]['user_name']
    user_phone = users[current_user.id]['user_phone']
    
    activity_no = request.form["activity_no"]
    condition = {"activity_no": ["=", activity_no]}
    data = CallDatabase.get_data("group_data", condition = condition, all_data = False)
    data += [user_name, user_phone]
    
    if len(request.form) == 1: # 按下我要報名
        return render_template("r_summary.html", html_data = data)
        
    else: # 按下確認報名
        activity_no = request.form["activity_no"]
        activity_name = request.form["activity_name"]
        activity_date = dt.datetime.strptime(request.form["activity_date"], '%Y-%m-%d').date()
        activity_type = request.form["activity_type"]
        
        attendee_name = request.form["attendee_name"]
        phone = request.form["phone"]
        user_id = current_user.id
        
        postgres_select_query = f"""SELECT condition FROM group_data WHERE activity_no = {activity_no}"""
        cursor.execute(postgres_select_query)
        activity_condition = cursor.fetchone()[0]
        print(activity_condition)
        
        #審核電話 先抓取該活動的報名者電話清單
        postgres_select_query = f"""SELECT phone FROM registration_data WHERE activity_no = '{activity_no}' ;"""
        cursor.execute(postgres_select_query)
        phone_registration = [data[0] for data in cursor.fetchall() if data[0] != None]

        print(f"phone_registration:{phone_registration}")
        
        if activity_condition == "closed":
            return render_template("r_summary_confirm.html", html_data = "失敗")
            
        elif phone in phone_registration:
            data.append("invalid")
            return render_template("r_summary.html", html_data = data)
            
        else:
            columns = ["activity_no", "activity_name", "attendee_name", "phone", "condition", "user_id", "activity_date", "activity_type"]
            values = [activity_no, activity_name, attendee_name, phone, "closed", user_id, activity_date, activity_type]
            CallDatabase.insert("registration_data", columns = columns, values = values)
            
            # 取得該活動目前報名人數
            postgres_select_query = f"""SELECT attendee, people FROM group_data WHERE activity_no = {activity_no}"""
            cursor.execute(postgres_select_query)

            attendee, people = cursor.fetchone() # 目前報名人數, 報名人數上限
            
            #將更新的報名人數attendee記錄到報名表單group_data裡
            columns = ["attendee"]
            values = [attendee + 1]
            condition = {"activity_no":["=", activity_no]}
            CallDatabase.update("group_data", columns = columns, values = values, condition = condition)

            #檢查報名人數attendee是否達上限people
            if (attendee + 1) == people:
                columns = ["condition"]
                values = ["closed"]
                condition = {"activity_no":["=", activity_no]}
                CallDatabase.update("group_data", columns = columns, values = values, condition = condition)
                
            return render_template("r_summary_confirm.html", html_data = "成功")
            
@app.route("/r_cancel", methods=['POST'])
def r_cancel():
    registration_no = request.form["registration_no"]
    activity_no = request.form["activity_no"]
    activity_name = request.form["activity_name"]
    user_id = current_user.get_id()
    
    condition = {"registration_no":["=", registration_no]}
    CallDatabase.delete("registration_data", condition = condition)
    
    # 取得該團的報名人數(attendee)
    condition = {"activity_no": ["=", activity_no]}
    attendee = CallDatabase.get_data("group_data", condition = condition, all_data = False)[15]

    #postgres_select_query = f"""SELECT attendee FROM group_data WHERE activity_no = {activity_no}"""
    #cursor.execute(postgres_select_query)
    #attendee = int(cursor.fetchone()[0])

    attendee -= 1
    
    condition_1 = {"activity_no":["=", activity_no]}
    condition_2 = {"activity_no":["=", activity_no], "condition":["=", "closed"]}
    CallDatabase.update("group_data", columns = ["attendee"], values = [attendee], condition =condition_1)
    CallDatabase.update("group_data", columns = ["condition"], values = ["pending"], condition = condition_2)
    
    return render_template("r_cancel.html", html_data = activity_name)

# 我的開團紀錄
@app.route("/my_group", methods=['GET', 'POST'])
@login_required
def my_group():
    if request.method == "GET":
        user_id = current_user.get_id()
        
        today_tw = (dt.datetime.now() + dt.timedelta(hours = 8)).date()
        condition_past = {"user_id":["=", current_user.get_id()], "activity_date":["<", today_tw], "condition":["!=", "initial"]}
        condition_now = {"user_id":["=", current_user.get_id()], "activity_date":[">=", today_tw], "condition":["!=", "initial"]}
        order = "activity_date"
        
        past_group_data = CallDatabase.get_data("group_data", condition = condition_past, order = order, ASC = False, all_data = True)
        now_group_data = CallDatabase.get_data("group_data", condition = condition_now, order = order, ASC = True, all_data = True)

        return render_template("my_group.html", html_data = [now_group_data, past_group_data])
        
    else:
        activity_no = request.form["activity_no"]
        
        condition = {"activity_no": ["=", activity_no]}    
        group_data = CallDatabase.get_data("group_data", condition = condition, all_data = False)

        attendee_data = CallDatabase.get_data("registration_data", condition = condition, all_data = True)
        
        return render_template("my_group_detail.html", html_data = [group_data, attendee_data])


# 我的報名紀錄
@app.route("/my_registration", methods=['GET', 'POST'])
@login_required
def my_registration():
    if request.method == "GET":
        user_id = current_user.get_id()
        
        today_tw = (dt.datetime.now() + dt.timedelta(hours = 8)).date()
        condition_past = {"user_id":["=", current_user.get_id()], "activity_date":["<", today_tw]}
        condition_now = {"user_id":["=", current_user.get_id()], "activity_date":[">=", today_tw]}
        order = "activity_date"
        
        past_registration_data = CallDatabase.get_data("registration_data", condition = condition_past, order = order, ASC = False, all_data = True)
        past_registration_data = list(set([(data[1], data[8], data[2]) for data in past_registration_data]))
        
        now_registration_data = CallDatabase.get_data("registration_data", condition = condition_now, order = order, ASC = True, all_data = True)
        now_registration_data = list(set([(data[1], data[8], data[2]) for data in now_registration_data]))

        return render_template("my_registration.html", html_data = [now_registration_data, past_registration_data])
        
    else:
        activity_no = request.form["activity_no"]

        condition = {"activity_no": ["=", activity_no]}
        group_data = CallDatabase.get_data("group_data", condition = condition, all_data = False)

        condition = {"activity_no": ["=", activity_no], "user_id":["=", current_user.id]}
        registration_data = CallDatabase.get_data("registration_data", condition = condition, all_data = True)

        return render_template("my_registration_detail.html", html_data = [group_data, registration_data])

# 聊天機器人 chatbot
@handler.add(MessageEvent, message = TextMessage)
def app_core(event):

    progress_list_fullgroupdata=[7, 1, 2, 3, 4, 5, 6 ,7 ]
    progress_list_halfgroupdata=[5, 1, 2, 3, 4, 5]
    progress_list_fullregistrationdata=[2, 0, 0, 0, 0, 0, 1, 2]

    print(f"event:{event}")
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    print("連接資料庫")

    if event.message.text == "~cancel":
        cancel.cancel(line_bot_api, cursor, conn, event)

    # 開始回答問題流程
    else:
        condition = {"condition": ["=", "initial"], "user_id":["=", event.source.user_id]}
        
        data_g = CallDatabase.get_data("group_data", condition = condition, all_data = False)
        print(f"data_g:{data_g}")
        column_all = ['acrivity_no', 'activity_type', 'activity_name',
                      'activity_date', 'activity_time', 'location_tittle', 'lat', 'long', 'people', 'cost',
                      'due_date', 'description', 'photo', 'name',
                      'phone', 'mail', 'attendee', 'condition', 'user_id']
    
        #準備寫入報名資料的那一列
        data_r = CallDatabase.get_data("registration_data", condition = condition, all_data = False)
        print(f"data_r:{data_r}")
        column_all_registration = ['registration_no', 'activity_no',
                                   'activity_name', 'attendee_name', 'phone',
                                   'mail', 'condition', 'user_id']
        
## ================
## 我要開團
## ================
        if data_g:
            i = data_g.index(None) # 寫入資料的那一格
            record = event.message.text
            #如果使用者輸入的資料不符合資料庫的資料型態, 則回覆 請重新輸入
            try:
                #輸入資料
                condition = {"condition": ["=", "initial"], "user_id":["=", event.source.user_id]}
                CallDatabase.update("group_data", columns = [column_all[i]], values = [record], condition = condition)
                
            except:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = "請重新輸入")
                )
            
            #如果還沒輸入到最後一格, 則繼續詢問下一題
            condition = {"condition": ["=", "initial"], "user_id":["=", event.source.user_id]}
            data_g = CallDatabase.get_data("group_data", condition = condition, all_data = False)
            print(f"輸入資料後 data_g:{data_g}")
        
            progress_target = progress_list_halfgroupdata if data_g[14] else progress_list_fullgroupdata

            if None in data_g: # 問下一題
                i = data_g.index(None)
                                
                msg = flexmsg_g.flex(i, data_g, progress_target)
                line_bot_api.reply_message(
                    event.reply_token,
                    msg)
                print("問下一題")
                    
            else: # summary
                msg = flexmsg_g.summary(data_g)
                line_bot_api.reply_message(
                    event.reply_token,
                    msg
                )
                        

## ================
## 我要報名
## ================
        elif data_r:
        
            if None in data_r:
                   
                i_r = data_r.index(None)
                record = event.message.text

                condition = {"condition": ["=", "initial"], "user_id":["=", event.source.user_id]}
                activity_no = CallDatabase.get_data("registration_data", condition = condition, all_data = False)[1] #取得正在報名的活動編號
                
                condition = {"activity_no": ["=", activity_no]}
                data = CallDatabase.get_data("registration_data", condition = condition, all_data = True)
                print(f"data:{data}")
                phone_registration = [row[4] for row in data] #取得報名該團的電話列表
                print(phone_registration, i_r, record)
                        
                    #當進行到輸入電話時(i_r==4)，開始檢驗是否重複
                if i_r == 4 and record in phone_registration:
                    #如果使用者輸入的電話重複則報名失敗，刪掉原本創建的列
                    condition = {"condition": ["=", "initial"], "user_id":["=", event.source.user_id]}
                    CallDatabase.dalete("registration_data", condition = condition)

                    line_bot_api.reply_message(
                        event.reply_token,
                        [TextSendMessage(text = "不可重複報名 請重新選擇想要報名的活動類型"), flexmsg_r.activity_type_for_attendee]
                    )
                    #~~~這邊感覺可以設計一個flex_msg，出現[返回]按鈕，重新回到報名第一步(按鈕回傳~join)

                else:
                    try:
                        # 輸入資料型態正確則更新
                        columns = [column_all_registration[i_r]]
                        values = [record]
                        condition = {"condition": ["=", "initial"], "user_id":["=", event.source.user_id]}
                        CallDatabase.update("registration_data", columns = columns, values = values, condition = condition)
       
                    except:
                        # 輸入資料型態錯誤則回應 "請重新輸入"
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text = "請重新輸入")
                        )

                # 檢查是否完成所有問題
                condition = {"condition": ["=", "initial"], "user_id":["=", event.source.user_id]}
                data_r = CallDatabase.get_data("registration_data", condition = condition, all_data = False) #準備寫入報名資料的那一列
                
                print("i_r = ",i_r)
                print("data_r = ",data_r)


                if None in data_r:
                
                    i_r = data_r.index(None)
                    msg = flexmsg_r.flex(i_r, progress_list_fullregistrationdata) #flexmsg需要新增報名情境
                    line_bot_api.reply_message(
                        event.reply_token,
                        msg
                    )
                    print("問下一題")
                    
                #出現summary
                elif None not in data_r:
                    msg = flexmsg_r.summary_for_attend(data_r)
                    line_bot_api.reply_message(
                        event.reply_token,
                        msg
                    )
    
#處理postback 事件，例如datetime picker
@handler.add(PostbackEvent)
def gathering(event):
    progress_list_fullgroupdata=[7, 1, 2, 3, 4, 5, 6 ,7]
    progress_list_halfgroupdata=[5, 1, 2, 3, 4, 5]
    progress_target = progress_list_fullgroupdata
    progress_list_fullregistrationdata=[2, 0, 0, 0, 0, 0, 1, 2]

    print(f"postback_event:{event}")
    
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    condition = {"condition": ["=", "initial"], "user_id":["=", event.source.user_id]}
    data_g = CallDatabase.get_data("group_data", condition = condition, all_data = False)
    
    postback_data = event.postback.data
    
    if postback_data == "~cancel":
        cancel.cancel(line_bot_api, cursor, conn, event)
        
## ================
## 我要開團
## ================
    elif postback_data == "我要開團":
        line_bot_api.reply_message(
            event.reply_token,
            flexmsg_g.activity_type
        )
        print("準備開團")

        #把只創建卻沒有寫入資料的列刪除
        cancel.reset(cursor, conn, event)
        
    elif "開團活動類型" in postback_data:
        #把只創建卻沒有寫入資料的列刪除
        cancel.reset(cursor, conn, event)
        
        type = postback_data.split("_")[1]
        print(f"type:{type}")

        #創建一列(condition = initial)
        columns = ["condition", "user_id", "activity_type", "attendee", "photo", "description"]
        values = ["initial", event.source.user_id, type, 1, "無", "無"]
        CallDatabase.insert("group_data", columns = columns, values = values)
            
        #撈主揪的資料
        condition = {"user_id": ["=", event.source.user_id], "condition": ["!=", "initial"]}
        data_for_basicinfo = CallDatabase.get_data("group_data", condition = condition, order = "activity_no", ASC = False, all_data = False)

        if data_for_basicinfo:
            columns = ["name", "phone"]
            values = [data_for_basicinfo[13], data_for_basicinfo[14]]
            condition = {"condition": ["=", "initial"], "user_id": ["=", event.source.user_id]}
            CallDatabase.update("group_data", columns = columns, values = values, condition = condition)
            progress_target = progress_list_halfgroupdata
        
        msg = flexmsg_g.flex(2, data = None, progress = progress_target)
        line_bot_api.reply_message(
            event.reply_token,
            msg
        )
        
    elif "修改開團" in postback_data:
        # 在summary點選修改後
        column = postback_data.split("_", 1)[1]

        columns = [column]
        values = ["Null"]
        condition = {"condition": ["=", "initial"], "user_id": ["=", event.source.user_id]}
        CallDatabase.update("group_data", columns = columns, values = values, condition = condition)
        
        progress_target = [7, 6, 6, 6, 6, 6, 6, 6]
        msg = flexmsg_g.flex(column, data_g, progress_target)
        line_bot_api.reply_message(
            event.reply_token,
            msg
        )
        
    elif "確認開團" in postback_data:
        
        columns = ["condition"]
        values = ["pending"]
        condition = {"condition": ["=", "initial"], "user_id": ["=", event.source.user_id]}
        CallDatabase.update("group_data", columns = columns, values = values, condition = condition)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "開團成功！")
        )
        
## ================
## 我要報名
## ================
    elif postback_data == "我要報名":
        line_bot_api.reply_message(
            event.reply_token,
            flexmsg_r.activity_type_for_attendee
        )
        print("準備可報名團資訊")
        
        #把只創建卻沒有寫入資料的列刪除
        cancel.reset(cursor, conn, event)
        
    # 按下rich menu中"我要報名" 選擇其中一種活動類型後
    elif "報名活動類型" in postback_data: #這裡的event.message.text會是上面quick reply回傳的訊息(四種type其中一種)
        type = postback_data.split("_")[1]
      
        today_tw = (dt.datetime.now() + dt.timedelta(hours = 8)).date()
        postgres_select_query = f"""SELECT * FROM group_data WHERE due_date >= '{today_tw}' AND activity_type = '{type}' AND people > attendee and condition = 'pending' ORDER BY activity_date ASC ;"""
        cursor.execute(postgres_select_query)
        data_carousel = cursor.fetchall()
        print(data_carousel)
        print(dt.date.today())
        print(today_tw)

        msg = flexmsg_r.carousel(data_carousel, type)
        line_bot_api.reply_message(
            event.reply_token,
            msg
        )

    elif "詳細資訊" in postback_data :
        record = postback_data.split("_")
        
        condition = {"activity_no":["=", record[0]]}
        data_tmp = CallDatabase.get_data("group_data", condition = condition, all_data = False)
        
        msg = flexmsg_r.MoreInfoSummary(data_tmp)

        line_bot_api.reply_message(
            event.reply_token,
            msg
        )

    elif "立即報名" in postback_data: #點了"立即報名後即回傳activity_no和activity_name"
        record = postback_data.split("_") #立即報名_{activity_no}_{type}_{name}_{date}
        activity_no, activity_type, activity_name, activity_date = record[1:]

        #把只創建卻沒有寫入資料的列刪除
        cancel.reset(cursor, conn, event)

        condition = {"condition": ["!=", "initial"], "user_id": ["=", event.source.user_id]}
        data_for_basicinfo = CallDatabase.get_data("registration_data", condition = condition, order = "registration_no", ASC = False, all_data = False)
        
        print("data_for_basicinfo = ", data_for_basicinfo)

        #審核電話 是否重複報名
        condition = {"activity_no": ["=", record[1]]}
        phone_registration = [data[4] for data in CallDatabase.get_data("registration_data", condition = condition) if data[4] != None]

        print(f"phone_registration:{phone_registration}")
            
        columns = ["activity_no", "activity_name", "condition", "user_id", "activity_date", "activity_type"]
        values = [activity_no, activity_name, "initial", event.source.user_id, activity_date, activity_type]
        CallDatabase.insert("registration_data", columns = columns, values = values)

        if data_for_basicinfo:
            if data_for_basicinfo[3] not in phone_registration:
                name, phone = data_for_basicinfo[3], data_for_basicinfo[4]

            condition = {"condition": ["=", "initial"], "user_id": ["=", event.source.user_id]}
            columns = ["attendee_name", "phone"]
            values = [name, phone]
            CallDatabase.update("registration_data", columns = columns, values = values, condition = condition)

        condition = {"condition": ["=", "initial"], "user_id": ["=", event.source.user_id]}
        data_r = CallDatabase.get_data("registration_data", condition = condition, all_data = False)
        print(data_r)

        if None in data_r:
            # 重新填寫報名資料
            i_r = data_r.index(None)
            print(f"count none in data_r = {data_r.count(None)}")
            print(f"i_r = {i_r}")
        
            msg = flexmsg_r.flex(i_r, progress_list_fullregistrationdata) #flexmsg需要新增報名情境
            line_bot_api.reply_message(
                event.reply_token,
                msg
            )

        else:
            # 已有報名紀錄則直接帶入先前資料
            msg = flexmsg_r.summary_for_attend(data_r)
            line_bot_api.reply_message(
                event.reply_token,
                msg
            )
            
    elif "修改報名" in postback_data:
        column = postback_data.split("_", 1)[1]  # attendee_name 或 phone
        
        columns = [column]
        values = ["Null"]
        condition = {"condition": ["=", "initial"], "user_id": ["=", event.source.user_id]}
        CallDatabase.update("registration_data", columns = columns, values = values, condition = condition)
        
        msg = flexmsg_r.flex(column, [2, 0, 0, 0, 0, 0, 1, 1])
        line_bot_api.reply_message(
            event.reply_token,
            msg
        )
        
    elif "確認報名" in postback_data:
        #找到他報的團的編號activity_no
        condition = {"condition": ["=", "initial"], "user_id": ["=", event.source.user_id]}
        activity_no = CallDatabase.get_data("registration_data", condition = condition, all_data = False)[1]

        #找報該團現在的報名人數attendee並更新(+1)
        condition = {"activity_no": ["=", activity_no]}
        temp = CallDatabase.get_data("group_data", condition = condition, all_data = False)

        attendee = temp[15]
        condition = temp[16]
        if condition == "closed":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text = "報名失敗")
            )
            
        else:
            attendee += 1

            #將更新的報名人數attendee記錄到報名表單group_data裡
            columns = ["attendee"]
            values = [attendee]
            condition = {"activity_no": ["=", activity_no]}
            CallDatabase.update("group_data", columns = columns, values = values, condition = condition)
            
            #檢查報名人數attendee是否達上限people
            condition = {"activity_no": ["=", activity_no]}
            people = CallDatabase.get_data("group_data", condition = condition, all_data = False)[8]

            if attendee == people:
                columns = ["condition"]
                values = ["closed"]
                condition = {"activity_no": ["=", activity_no]}
                CallDatabase.update("group_data", columns = columns, values = values, condition = condition)

            #將報名表單的condition改成closed
            columns = ["condition"]
            values = ["closed"]
            condition = {"condition": ["=", "initial"], "user_id": ["=", event.source.user_id]}
            CallDatabase.update("registration_data", columns = columns, values = values, condition = condition)
            
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text = "報名成功！")
            )

            cursor.close()
            conn.close()

## ================
## 我的開團
## ================
    elif postback_data == "我的開團":
        line_bot_api.reply_message(
            event.reply_token,
            flexmsg_glist.list_type
        )
        print("查詢開團紀錄")
        cancel.reset(cursor, conn, event)
        
    elif "開團紀錄" in postback_data:
        
        type = postback_data.split("_")[1]
        
        today_tw = (dt.datetime.now() + dt.timedelta(hours = 8)).date()
        condition = {"condition": ["!=", "initial"], "user_id": ["=", event.source.user_id, ]}
        if type == "已結束":
            condition["activity_date"] = ["<", today_tw]
        elif type == "進行中":
            condition["activity_date"] = [">=", today_tw]
            
        group_data = CallDatabase.get_data("group_data", condition = condition, order = "activity_date", all_data = True)
        print(f"group_data:{group_data}")

        msg = flexmsg_glist.glist(group_data, type)
        line_bot_api.reply_message(
        event.reply_token,
        msg
        )
        
    elif "開團資訊" in postback_data:
        activity_no = postback_data.split("_")[1]
        
        condition = {"activity_no": ["=", activity_no]}
        group_data = CallDatabase.get_data("group_data", condition = condition, all_data = False)

        print("group_data = ", group_data)
        
        msg = flexmsg_glist.MyGroupInfo(group_data)
        line_bot_api.reply_message(
            event.reply_token,
            msg
            )
            
    #主揪查看報名者資訊(報名者暱稱、電話)
    elif "報名者資訊" in postback_data:
        activity_no = postback_data.split("_")[1]

        condition = {"activity_no": ["=", activity_no]}
        temp = CallDatabase.get_data("registration_data", condition = condition, all_data = False)

        if temp:
            activity_name = temp[2]
            print("activity_name = ", activity_name)

            condition = {"activity_no": ["=", activity_no]}
            attendee_data = [f"{data[3]} {data[4]}" for data in CallDatabase.get_data("registration_data", condition = condition)]
 
            print("attendee_data = ", attendee_data)
            
            msg = f"{activity_name}" + "\n報名者資訊：\n" + "\n".join(attendee_data)
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
        activity_no = postback_data.split("_")[1]
        
        columns = ["condition"]
        values = ["closed by owner"]
        condition = {"activity_no": ["=", activity_no]}
        CallDatabase.update("group_data", columns = columns, values = values, condition = condition)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "成功結束報名！")
            )
       
## ================
## 我的報名
## ================
    elif postback_data == "我的報名":
        line_bot_api.reply_message(
            event.reply_token,
            flexmsg_rlist.list_type
        )
        print("查詢報名紀錄")
        cancel.reset(cursor, conn, event)
        
    elif "報名紀錄" in postback_data:
    
        type = postback_data.split("_")[1]
        
        today_tw = (dt.datetime.now() + dt.timedelta(hours = 8)).date()
        condition = {"condition": ["!=", "initial"], "user_id": ["=", event.source.user_id, ]}
        if type == "已結束":
            condition["activity_date"] = ["<", today_tw]
        elif type == "進行中":
            condition["activity_date"] = [">=", today_tw]
              
        rg_data = CallDatabase.get_data("registration_data", condition = condition, order = "activity_date", all_data = True)
        if rg_data:
            #activity_no, activity_name, activity_date
            rg_data = [(data[1], data[2], data[7]) for data in rg_data] 
            rg_data = sorted(list(set(rg_data)), key = lambda x: x[2])
        
        print(f"rg_data:{rg_data}")

        msg = flexmsg_rlist.rlist(rg_data, type)
        line_bot_api.reply_message(
        event.reply_token,
        msg
        )
    
    # 在報名列表 點選活動
    elif "查報名" in postback_data:
        activity_no = postback_data.split('_')[0]
        
        #根據回傳的activity_no，從group_data裡找到活動資訊
        condition = {"activity_no": ["=", activity_no]}
        group_info = CallDatabase.get_data("group_data", condition = condition, all_data = False)

        #根據回傳的activity_no和user_id找到報名資訊(可能不只一列)
        condition = {"activity_no": ["=", activity_no], "user_id": ["=", event.source.user_id]}
        registration_info = CallDatabase.get_data("registration_data", condition = condition, all_data = True)
        
        msg = flexmsg_rlist.carousel_registration(group_info, registration_info)
        line_bot_api.reply_message(
            event.reply_token,
            msg
        )
        
    elif "取消報名" in postback_data: #按下取消報名按鈕將回傳(record_activity_取消報名)
        registration_no = postback_data.split('_')[0]
        activity_no = postback_data.split('_')[1]
        # 刪除報名
        condition = {"registration_no": ["=", registration_no], "user_id": ["=", event.source.user_id]}
        CallDatabase.delete("registration_data", condition = condition)

        #找報該團現在的報名人數attendee並更新(-1)
        postgres_select_query = f"""SELECT attendee FROM group_data WHERE activity_no = {activity_no};"""
        cursor.execute(postgres_select_query)
        attendee = cursor.fetchone()[0]
        attendee -= 1

        #將更新的報名人數attendent記錄到報名表單group_data裡
        postgres_update_query = f"""UPDATE group_data SET attendee = {attendee} WHERE activity_no = {activity_no};"""
        cursor.execute(postgres_update_query)
        conn.commit()

        #更新該活動的condition(=pending)
        postgres_update_query = f"""UPDATE group_data SET condition = 'pending' WHERE activity_no = {activity_no};"""
        cursor.execute(postgres_update_query)
        conn.commit()

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "取消成功！")
        )

## ================
## 上下頁
## ================
    elif "forward" in postback_data or "backward" in postback_data:
        
        record = postback_data.split("_") #record[0] = forward, reocord[1] = command
        type = record[2]
        i = int(record[3])

        # [我要報名] 活動列表的下一頁
        today_tw = (dt.datetime.now() + dt.timedelta(hours = 8)).date()
        if record[1] == "activity":
            #record[2] = activity_type, record[3] = i
            postgres_select_query = f"""SELECT * FROM group_data WHERE due_date >= '{today_tw}' AND activity_type = '{record[2]}' and people > attendee and condition = 'pending' ORDER BY activity_date ASC;"""
           
            cursor.execute(postgres_select_query)
            data = cursor.fetchall()
            print(f"data:{data}")
            msg = flexmsg_r.carousel(data, type, i)

        # [我的開團]、[我的報名] 列表的下一頁
        elif record[1] in ["glist", "rlist"] :
            #record[2] = 進行中或已結束, record[3] = i
            if type == "已結束":
                condition = {"user_id": ["=", event.source.user_id], "activity_date": ["<", today_tw]}
            elif type == "進行中":
                condition = {"user_id": ["=", event.source.user_id], "activity_date": [">=", today_tw]}
                
            if record[1] == "glist":
                data = CallDatabase.get_data("group_data", condition = condition, order = "activity_date", all_data = True)
                msg = flexmsg_glist.glist(data, type, i)
            elif record[1] == "rlist":
                data = CallDatabase.get_data("registration_data", condition = condition, order = "activity_date", all_data = True)
                data = sorted(list(set(data)), key = lambda x: x[7])
                msg = flexmsg_rlist.rlist(data, type, i)
        
        line_bot_api.reply_message(
            event.reply_token,
            msg
            )
## ================
## 天氣預報
## ================
    elif "climate" in postback_data:
        mapbox_key = config.get("mapbox", "access_token")
        climate_key = config.get("climate", "authorization")

        activity_no = postback_data.split("_")[1]
        condition = {"activity_no": ["=" ,activity_no]}
        g_data = CallDatabase.get_data("group_data", condition = condition, all_data = False)
        longtitude, latitude = g_data[7], g_data[6]

        try:
            #geo_data
            url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{longtitude},{latitude}.json"
            my_params = {"language": "zh-tw", "access_token": mapbox_key}
            re_mapbox = requests.get(url, params = my_params)
            county = re_mapbox.json()["features"][0]["context"][-2]["text"]
            district = re_mapbox.json()["features"][0]["context"][-3]["text"]
            print(county, district)

            #climate_data
            county_code = {'宜蘭縣': 'F-D0047-003', '桃園市': 'F-D0047-007', '新竹縣': 'F-D0047-011', '苗栗縣': 'F-D0047-015', '彰化縣': 'F-D0047-019', '南投縣': 'F-D0047-023', '雲林縣': 'F-D0047-027', '嘉義縣': 'F-D0047-031', '屏東縣': 'F-D0047-035', '臺東縣': 'F-D0047-039', '花蓮縣': 'F-D0047-043', '澎湖縣': 'F-D0047-047', '基隆市': 'F-D0047-051', '新竹市': 'F-D0047-055', '嘉義市': 'F-D0047-059', '臺北市': 'F-D0047-063', '高雄市': 'F-D0047-067', '新北市': 'F-D0047-071', '臺中市': 'F-D0047-075', '臺南市': 'F-D0047-079', '連江縣': 'F-D0047-083', '金門縣': 'F-D0047-087'}
            climate_url = f"https://opendata.cwb.gov.tw/api/v1/rest/datastore/{county_code.get(county)}"
            my_params = {"Authorization": climate_key, "locationName": district}

            re_climate = requests.get(climate_url, params = my_params).json()
            weather_element = re_climate["records"]["locations"][0]["location"][0]["weatherElement"]
            UVI = weather_element.pop(9)

            start_time = dt.datetime.strptime(weather_element[0]["time"][0]["startTime"], "%Y-%m-%d %H:%M:%S")
            dt_list = [start_time] + [dt.datetime.strptime(time["endTime"], "%Y-%m-%d %H:%M:%S") for time in weather_element[0]["time"]]

            activity_date, activity_time = g_data[3], g_data[4]
            activity_dt = dt.datetime.strptime(str(activity_date) + str(activity_time), "%Y-%m-%d%H:%M:%S")

            i = 0
            while i < len(dt_list) - 1:
                if dt_list[i] <=  activity_dt < dt_list[i+1]:
                    break
                else:
                    i += 1
            print(i)

            if i == len(dt_list) - 1:
                print("僅提供一週內的天氣預報！")
                msg = flexmsg_climate.no_climate()

            else:
                climate_data = {item["description"]: list(item["time"][i]["elementValue"][0].values()) for item in weather_element}
                UVI = {item["startTime"].split()[0]:[[row["value"], row["measures"]] for row in item["elementValue"]] for item in UVI["time"]}
                uvi = [row[0] for row in UVI.get(str(activity_date), [])]
                print(activity_dt, weather_element[0]["time"][i], climate_data, end = "\n")
                
                climate_lst = ["12小時降雨機率", "天氣現象", "平均溫度", "最高溫度", "最低溫度", "平均相對濕度", "風向", "最大風速"]
                rain, weather, temperature_avg, temperature_max, temperature_min, humidity, wind_d, wind_v = [climate_data[item][0] for item in climate_lst]
                
                msg = flexmsg_climate.climate(activity_date, county, district, rain, weather, temperature_avg, temperature_max, temperature_min, humidity, wind_d, wind_v, uvi)
        except:
             msg = flexmsg_climate.no_data()

        line_bot_api.reply_message(
            event.reply_token,
            msg
        )

## ================
## 開團回傳時間
## ================
    else:
        #開團時,填寫時間資料
        i = data_g.index(None)
        print("i =",i)
        column_all = ['acrivity_no', 'activity_type', 'activity_name',
                      'activity_date', 'activity_time', 'location_tittle', 'lat', 'long', 'people', 'cost',
                      'due_date', 'description', 'photo', 'name',
                      'phone', 'mail', 'attendee', 'condition', 'user_id']
        #處理activity date and time
        if event.postback.data == "activity_time" :

            record = event.postback.params['datetime']
            record = record.split("T")
            print(record)
            due_default = dt.datetime.strptime(record[0], "%Y-%m-%d") - dt.timedelta(days=1) #due_date
            # 寫入資料(更新活動日期、時間，預填截止時間）
            condition = {"condition": ["=", "initial"], "user_id":["=", event.source.user_id]}
            CallDatabase.update("group_data", columns = ["activity_date", "activity_time", "due_date"], values = [record[0], record[1], due_default], condition = condition)

            #處理due date
        elif event.postback.data == "due_time":

            record = event.postback.params['date']
            # 寫入資料(更新截止時間)
            condition = {"condition": ["=", "initial"], "user_id":["=", event.source.user_id]}
            CallDatabase.update("group_data", columns = ["due_date"], values = [record], condition = condition)

        condition = {"condition": ["=", "initial"], "user_id":["=", event.source.user_id]}
        data_g = CallDatabase.get_data("group_data", condition = condition, all_data = False)
        print(data_g)
        
        if data_g[14]:
            progress_target = progress_list_halfgroupdata
            
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

@handler.add(MessageEvent, message = LocationMessage)
def gathering(event):
    progress_list_fullgroupdata=[7, 1, 2, 3, 4, 5, 6 ,7 ]
    progress_list_halfgroupdata=[5, 1, 2, 3, 4, 5]
    progress_target = progress_list_fullgroupdata
    
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    condition = {"condition": ["=", "initial"], "user_id":["=", event.source.user_id]}
    data_g = CallDatabase.get_data("group_data", condition = condition, all_data = False)
    
    i = data_g.index(None)
    print("i =",i)

    record = [event.message.title, event.message.latitude, event.message.longitude]
    if record[0] == None:
        record[0] = event.message.address[:50]
    # 寫入資料(更新位置資訊)
    condition = {"condition": ["=", "initial"], "user_id":["=", event.source.user_id]}
    CallDatabase.update("group_data", columns = ["location_tittle", "lat", "long"], values = [record[0], record[1], record[2]], condition = condition)
    
    condition = {"condition": ["=", "initial"], "user_id":["=", event.source.user_id]}
    data_g = CallDatabase.get_data("group_data", condition = condition, all_data = False)
    print(data_g)
    
    if data_g[14]:
        progress_target = progress_list_halfgroupdata
    
    if None in data_g:
        i = data_g.index(None)
        msg = flexmsg_g.flex(i, data_g, progress_target)
        line_bot_api.reply_message(
            event.reply_token,
            msg)
    elif None not in data_g:
        msg = flexmsg_g.summary(data_g)
        print(msg)
        line_bot_api.reply_message(
            event.reply_token,
            msg
        )
    cursor.close()
    conn.close()
    

@handler.add(MessageEvent, message = ImageMessage)
def pic(event):
    condition = {"condition": ["=", "initial"], "user_id": ["=", event.source.user_id]}
    data_g = CallDatabase.get_data("group_data", condition = condition, all_data = False) 
  
    if data_g:
        i = data_g.index(None)
        print("i =",i)
        if i == 12:

            #把圖片存下來並傳上去
            ext = 'jpg'
            message_content = line_bot_api.get_message_content(event.message.id)

            file_path = f"/tmp/{event.message.id}.png"
            with open(file_path, "wb") as tf:
                for chunk in message_content.iter_content():
                    tf.write(chunk)
                tempfile_path = tf.name
            
            dist_path = tempfile_path
            dist_name = os.path.basename(dist_path)
            print(f"dist_path={dist_path}", "\n", f"dist_name={dist_name}")

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

                image = client.upload_from_path(dist_path, config = con, anon = False)
                os.remove(dist_path)
                print("image = ",image)
                #把圖片網址存進資料庫
                condition = {"condition": ["=", "initial"], "user_id": ["=", event.source.user_id]}
                columns = ["photo"]
                values = [image['link']]
                CallDatabase.update("group_data", columns = columns, values = values, condition = condition)
                
                print(image['link'])

                condition = {"condition": ["=", "initial"], "user_id": ["=", event.source.user_id]}
                data_g = CallDatabase.get_data("group_data", condition = condition, all_data = False) 
                
                msg = [TextSendMessage(text='上傳成功！'), flexmsg_g.summary(data_g)]

            except:
                msg = [TextSendMessage(text='上傳失敗！'), flexmsg_g.summary(data_g)]
                
            line_bot_api.reply_message(
                event.reply_token,
                msg
            )

    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "現在不用傳圖片給我")
        )
    return 0


if __name__ == "__main__":
    app.run()
