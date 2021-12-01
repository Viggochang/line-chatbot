from models import CallDatabase
from templates import flexmsg_activity
from controllers import reset, basic_info, verify, update_photo
from linebot.models import TextSendMessage
import datetime as dt

def choose_activity_type(user_id):
    reset.reset(user_id)
    msg = flexmsg_activity.activity_type()
    return msg

def new_activity(line_id, user_id, activity_type, user_info, user_condition, init_condition):
    if not user_id:
        CallDatabase.insert("users", columns = ["line_id"], values = [line_id])  
        user_id = CallDatabase.get_data("users", ["id"], condition = user_condition, all_data = False)[0]
        init_condition = ["condition = 'initial'", f"user_id = {user_id}"]

    #創建一列(condition = initial)
    columns = ["condition", "user_id", "activity_type", "attendee", "photo", "description"]
    values = ["initial", user_id, activity_type, 0, "無", "無"]
    CallDatabase.insert("activity", columns = columns, values = values)

    activity_info = basic_info.basic_info(init_condition)[0]
    data_activity = activity_info + user_info
    #回傳問題
    progress_activity = 5 if data_activity[13] else 7 #to-do 進度條待改
    msg = verify.next_msg("activity", data_activity, progress_activity)
    return msg

def after_replay_activity_time(activity_date, activity_time, init_condition, user_info):
    # 預設 due_date 為 activity_date 的前一天
    due_date_default = dt.datetime.strptime(activity_date, "%Y-%m-%d") - dt.timedelta(days=1)
    
    columns = ["activity_date", "activity_time", "due_date"]
    values = [activity_date, activity_time, due_date_default]
    CallDatabase.update("activity", columns = columns, values = values, condition = init_condition)
    
    activity_info = basic_info.basic_info(init_condition)[0]
    data_activity = activity_info + user_info

    progress_activity = 5 if data_activity[13] else 7 #to-do 進度條待改
    msg = verify.next_msg("activity", data_activity, progress_activity)
    return msg

def after_replay_due_date(due_date, init_condition, user_info):
    CallDatabase.update("activity", columns = ["due_date"], values = [due_date], condition = init_condition)
    activity_info = basic_info.basic_info(init_condition)[0]
    data_activity = activity_info + user_info

    msg = verify.next_msg("activity", data_activity)   
    return msg

def after_replay_location(position, latitude, longitude, address, init_condition, user_info):
    if position == None:
        position = address[:50]

    CallDatabase.update("activity", columns = ["location_title", "location_latitude", "location_longitude"], values = [position, latitude, longitude], condition = init_condition)
    
    activity_info = basic_info.basic_info(init_condition)[0]
    data_activity = activity_info + user_info

    progress_activity = 5 if data_activity[13] else 7 #to-do 進度條待改
    msg = verify.next_msg("activity", data_activity, progress_activity)  #to-do 進度條待改
    return msg

def after_replay_photo(photo_content, imgur_config, user_info, activity_info, init_condition, user_id):
    msg_text = update_photo.photo(photo_content, imgur_config, activity_info, init_condition, user_id)
    msg = [TextSendMessage(text = msg_text)]
    
    if msg_text != "現在不用傳圖片給我！":
        activity_info = basic_info.basic_info(init_condition)[0]
        data_activity = activity_info + user_info    
        msg.append(verify.next_msg("activity", data_activity))   
        
    return msg     

def confirm_new_activity(init_condition):
    CallDatabase.update("activity", columns = ["condition"], values = ["pending"], condition = init_condition)
    msg = TextSendMessage(text = "開團成功！")  
    return msg

def cancel_new_activity(init_condition):
    CallDatabase.update("activity", columns = ["condition"], values = ["delete"], condition = init_condition)
    msg = TextSendMessage(text = "取消成功！")  
    return msg   
