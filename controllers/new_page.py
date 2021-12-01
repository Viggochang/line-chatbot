from models import CallDatabase
from templates import flexmsg_registration, flexmsg_record

def new_page(button_type, i, record_type, today_tw, user_id):
    all_activity_type = ["登山踏青", "桌遊麻將", "吃吃喝喝", "唱歌跳舞"]
    
    # [我要報名] 可報名列表的上下頁
    if button_type in all_activity_type:
        # 篩選可以報名的團
        condition = [f"due_date >= '{today_tw}'", f"activity_type = '{button_type}'", "people > attendee", "condition = 'pending'"]
        data_carousel = CallDatabase.get_data("activity", condition = condition, order = "activity_date")
        # 回傳 下一頁或上一頁的列表
        msg = flexmsg_registration.carousel(data_carousel, button_type, i)

    # [我的開團]、[我的報名] 列表的下一頁
    else:
        condition = ["condition IN ('closed', 'closed by owner', 'pending')", f"user_id = '{user_id}'"]
        
        # 我的開團紀錄
        if record_type == "開團紀錄":
            condition.append(f"activity_date < '{today_tw}'") if button_type == "已結束" else condition.append(f"activity_date >= '{today_tw}'")
            activity_info = CallDatabase.get_data("activity", ["id", "activity_name"], condition = condition, order = "activity_date", all_data = True)
            msg = flexmsg_record.record_list("開團", activity_info, button_type, i)
        
        # 我的報名紀錄
        elif record_type == "報名紀錄":
            # 取得報名紀錄   
            registration_data = CallDatabase.get_data("registration", ["activity_id", "id"], condition = condition,  all_data = True)
            all_activity_id = [data[0] for data in registration_data]
            activity_name_date = [CallDatabase.get_data("activity", ["activity_name", "activity_date"], condition = [f"id = {activity_id}"], all_data = False) for activity_id in all_activity_id]
            registration_data = [data[0] + list(data[1]) for data in zip(registration_data, activity_name_date)]  # activity_id, registration_id, activity_name
            if button_type == "已結束":
                registration_data = [data for data in registration_data if data[3] < today_tw]
            else:
                registration_data = [data for data in registration_data if data[3] >= today_tw]
            registration_data = sorted(registration_data, key = lambda x:x[3])    
            # 回傳回傳報名列表
            msg = flexmsg_record.record_list("報名", registration_data, button_type, i)

    return msg
