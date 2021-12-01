from models import CallDatabase
from templates import flexmsg_record
from controllers import reset
from linebot.models import TextSendMessage

def choose_record_type(user_id, status):
    reset.reset(user_id)
    msg = flexmsg_record.record_type(status)
    return msg

def activity_record(user_id, record_type, today_tw):
    # 依照活動時間篩選為已結束或進行中
    if user_id:
        condition = ["condition <> 'initial'", f"user_id = '{user_id}'"]
        condition.append(f"activity_date < '{today_tw}'") if record_type == "已結束" else condition.append(f"activity_date >= '{today_tw}'")

        # 取得開團紀錄
        activity_info = CallDatabase.get_data("activity", ["id", "activity_name"], condition = condition, order = "activity_date", all_data = True)
        msg = flexmsg_record.record_list("開團", activity_info, record_type)
    else:
        msg = flexmsg_record.record_list("開團", None, record_type)  
    return msg

def registration_record(user_id, record_type, today_tw):
    # 依照活動時間篩選為已結束或進行中
    if user_id:
        condition = ["condition = 'closed'", f"user_id = '{user_id}'"]
        
        # 取得報名紀錄   
        registration_data = CallDatabase.get_data("registration", ["activity_id", "id"], condition = condition,  all_data = True)
        all_activity_id = [data[0] for data in registration_data]
        activity_name_date = [CallDatabase.get_data("activity", ["activity_name", "activity_date"], condition = [f"id = {activity_id}"], all_data = False) for activity_id in all_activity_id]
        registration_data = [data[0] + list(data[1]) for data in zip(registration_data, activity_name_date)]  # activity_id, registration_id, activity_name
        if record_type == "已結束":
            registration_data = [data for data in registration_data if data[3] < today_tw]
        else:
            registration_data = [data for data in registration_data if data[3] >= today_tw]
        registration_data = sorted(registration_data, key = lambda x:x[3])    
        # 回傳回傳報名列表
        print(registration_data)  # activity_id, registration_id, activity_name, activity_date
        msg = flexmsg_record.record_list("報名", registration_data, record_type) 
    else:
        msg = flexmsg_record.record_list("報名", None, record_type) 
    return msg

def activity_information(activity_id):
    condition = [f"id = {activity_id}"]
    activity_info = CallDatabase.get_data("activity", condition = condition, all_data = False)
    
    # 回傳活動資訊
    msg = flexmsg_record.send_activity_info(activity_info)    
    return msg

def attendee_information(activity_id):
    condition = [f"id = {activity_id}"]
    activity_name = CallDatabase.get_data("activity", ["activity_name"], condition = condition, all_data = False)[0]

    # 取得該團的報名資訊
    condition = [f"activity_id = {activity_id}", f"condition = 'closed'"]
    all_attendee_id = [data[0] for data in CallDatabase.get_data("registration", ["user_id"], condition = condition)]
    attendee_data = [CallDatabase.get_data("users", ["name", "phone"], condition = [f"id = {attendee_id}"], all_data = False) for attendee_id in all_attendee_id]
    
    msg = flexmsg_record.attendee_info(activity_name, attendee_data)    
    return msg

def activity_registration_information(activity_id, registration_id, user_condition):
     # 根據回傳的 activity_id，從 activity 裡找到活動資訊
    condition = [f"id = {activity_id}"]
    activity_data = CallDatabase.get_data("activity", condition = condition, all_data = False)
    
    # 取得 owner 資料
    condition = [f"id = {activity_data[15]}"]
    owner_info = CallDatabase.get_data("users", ["name", "phone"], condition = condition, all_data = False)

    # 取得 user 資料
    user_info = CallDatabase.get_data("users", ["name", "phone"], condition = user_condition, all_data = False)
    
    # 回傳活動資訊及報名資訊
    msg = flexmsg_record.activity_registration_info(activity_data, owner_info, user_info, registration_id)
    return msg

def close_activity(activity_id):
    condition = [f"id = {activity_id}"]
    CallDatabase.update("activity", columns = ["condition"], values = ["closed by owner"], condition = condition)

    # 回應 成功結束報名
    msg = TextSendMessage(text = "成功結束報名！")   
    return msg
