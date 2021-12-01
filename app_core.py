from __future__ import unicode_literals
from flask import Flask, request, abort
import configparser  
import datetime as dt

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageSendMessage, PostbackEvent, LocationMessage, ImageMessage

from controllers import basic_info, text_insert, new_activity, new_registration, record, edit, verify, climate, new_page

app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read("config.ini")

line_bot_api = LineBotApi(config.get("line-bot", "channel_access_token"))
handler = WebhookHandler(config.get("line-bot", "channel_secret"))
mapbox_key = config.get("mapbox", "access_token")
climate_key = config.get("climate", "authorization")

today_tw = (dt.datetime.now() + dt.timedelta(hours = 8)).date()

# 接收 LINE 的資訊
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print(f"event_body:{body}")

    global line_id, user_condition
    line_id = basic_info.line_id(request.get_data())
    user_condition = [f"line_id = '{line_id}'"]

    global user_id, init_condition
    user_id = basic_info.user_id(user_condition)
    init_condition = ["condition = 'initial'"]
    init_condition.append(f"user_id = {user_id}" if user_id else f"user_id = Null")

    global activity_info, user_info, registration_info
    activity_info, registration_info = basic_info.basic_info(init_condition)
    user_info = basic_info.user_info(user_condition)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'
  

@handler.add(MessageEvent, message = TextMessage)
def message_event(event):
    user_text = event.message.text

    msg = text_insert.text_insert(user_text, user_id, activity_info, user_info, registration_info, init_condition, user_condition)

    line_bot_api.reply_message(
        event.reply_token,
        msg
    )    

@handler.add(PostbackEvent)
def postback_event(event):
    postback_data = event.postback.data

    if postback_data == "我要開團":
        msg = new_activity.choose_activity_type(user_id)

    elif "開團活動類型" in postback_data:
        activity_type = postback_data.split("_")[1]
        
        msg = new_activity.new_activity(line_id, user_id, activity_type, user_info, user_condition, init_condition)

    elif "回覆活動時間" in postback_data:
        activity_date, activity_time = event.postback.params["datetime"].split("T")
        
        msg = new_activity.after_replay_activity_time(activity_date, activity_time, init_condition, user_info)

    elif "回覆報名截止時間" in postback_data:
        due_date = event.postback.params["date"]

        msg = new_activity.after_replay_due_date(due_date, init_condition, user_info)

    elif "修改" in postback_data:
        table, column = postback_data.split("_", 2)[1:]

        msg = edit.edit(table, column, init_condition, user_condition, activity_info)

    elif "確認開團" in postback_data:
        msg = new_activity.confirm_new_activity(init_condition)

    elif "取消開團" in postback_data:
        msg = new_activity.cancel_new_activity(init_condition)
#-------------------------------------------------------------------------------------
    elif postback_data == "我要報名":
        msg = new_registration.choose_activity_type(user_id)
        
    elif "報名活動類型" in postback_data: 
        activity_type = postback_data.split("_")[1]
      
        msg = new_registration.activity_for_registration(today_tw, activity_type)

    elif "詳細資訊" in postback_data :
        activity_id = postback_data.split("_")[1]
        
        msg = new_registration.activity_detail(activity_id)

    elif "立即報名" in postback_data: 
        activity_id = postback_data.split("_")[1]

        msg = new_registration.new_registration(line_id, user_id, activity_id, user_info, user_condition, init_condition)

    elif "確認報名" in postback_data:
        activity_id = postback_data.split("_")[1]

        msg = new_registration.confirm_registration(activity_id, init_condition)

    elif "取消報名" in postback_data: 
        registration_id, activity_id = postback_data.split('_')[1:]

        msg = new_registration.cancel_registration(registration_id, activity_id)
#-------------------------------------------------------------------------------------
    elif postback_data == "我的開團":
        status = "開團" 

        msg = record.choose_record_type(user_id, status)

    elif "開團紀錄" in postback_data:  
        record_type = postback_data.split("_")[1] 

        msg = record.activity_record(user_id, record_type, today_tw)
        
    elif "開團資訊" in postback_data:
        activity_id = postback_data.split("_")[1]

        msg = record.activity_information(activity_id)
            
    #主揪查看報名者資訊(報名者暱稱、電話)
    elif "報名者資訊" in postback_data:
        activity_id = postback_data.split("_")[1]

        msg = record.attendee_information(activity_id)

    #主揪提早關團
    elif "結束報名" in postback_data:
        activity_id = postback_data.split("_")[1]
        
        msg = record.close_activity(activity_id)
#-------------------------------------------------------------------------------------
    elif postback_data == "我的報名":
        status = "報名"

        msg = record.choose_record_type(user_id, status)
        
    elif "報名紀錄" in postback_data:
        record_type = postback_data.split("_")[1]

        msg = record.registration_record(user_id, record_type, today_tw)

    elif "查報名" in postback_data:
        activity_id, registration_id = postback_data.split('_')[1:]

        msg = record.activity_registration_information(activity_id, registration_id, user_condition)
#-------------------------------------------------------------------------------------
    elif "newPage" in postback_data:
        button_type, i, record_type = postback_data.split("_")[0:3]
        i = int(i)  # i代表要從資料庫中第幾個資料開始呈現，下一頁的 i=i+8，上一頁的 i=i-8

        msg = new_page.new_page(button_type, i, record_type, today_tw, user_id)
#-------------------------------------------------------------------------------------
    elif "climate" in postback_data:
        activity_id = postback_data.split("_")[1]

        location_longitude, location_latitude, activity_date, activity_time = climate.location_datetime(activity_id)

        county, district = climate.geo_data(mapbox_key, location_longitude, location_latitude)
        
        msg = climate.climate(climate_key, county, district, activity_date, activity_time)

    line_bot_api.reply_message(
        event.reply_token,
        msg
    )

@handler.add(MessageEvent, message = LocationMessage)
def location(event):
    # 取得地點名稱、經度、緯度, 如果該地點沒有名稱，則用地址取代
    location_info = event.message
    position, latitude, longitude, address = location_info.title, location_info.latitude, location_info.longitude, location_info.address 
    
    msg = new_activity.after_replay_location(position, latitude, longitude, address, init_condition, user_info)

    line_bot_api.reply_message(
        event.reply_token,
        msg
    )

@handler.add(MessageEvent, message = ImageMessage)
def pic(event):
    photo_content = line_bot_api.get_message_content(event.message.id)
    imgur_config = [config.get('imgur', 'client_id'), config.get('imgur', 'client_secret'), config.get('imgur', 'access_token'), config.get('imgur', 'refresh_token'), config.get('imgur', 'album_id')]

    msg = new_activity.after_replay_photo(photo_content, imgur_config, user_info, activity_info, init_condition, user_id)

    line_bot_api.reply_message(
        event.reply_token,
        msg
    )

if __name__ == "__main__":
    app.run()
    