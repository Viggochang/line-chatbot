from models import CallDatabase
from templates import flexmsg_registration
from controllers import reset, basic_info, verify
from linebot.models import TextSendMessage


def choose_activity_type(user_id):
    reset.reset(user_id)
    msg = flexmsg_registration.activity_type()
    return msg

def activity_for_registration(today_tw, activity_type):
    # 篩選可以報名的團
    condition = [f"due_date >= '{today_tw}'", f"activity_type = '{activity_type}'", "people > attendee", "condition = 'pending'"]
    data_carousel = CallDatabase.get_data("activity", condition = condition, order = "activity_date")
    
    #傳可報名的團的選單
    msg = flexmsg_registration.carousel(data_carousel, activity_type)    
    return msg

def activity_detail(activity_id):
    #根據該活動的編號找出活動資訊
    condition = [f"id = {activity_id}"]
    activity_info = basic_info.basic_info(condition)[0]
    owner_user_id = CallDatabase.get_data("activity", ["user_id"], condition = condition, all_data = False)[0]
    
    condition = [f"id = {owner_user_id}"]
    owner_user_info = CallDatabase.get_data("users", ["name", "phone"], condition = condition, all_data = False)

    activity_info = activity_info + owner_user_info
    
    # 回傳該團活動資訊
    msg = flexmsg_registration.more_info(activity_info, activity_id) 
    return msg

def new_registration(line_id, user_id, activity_id, user_info, user_condition, init_condition):

    if user_id and verify.duplicate_registration(activity_id, user_id):
        print("報名重複")
        msg = flexmsg_registration.duplication()
    
    else:
        if not user_id:
            CallDatabase.insert("users", columns = ["line_id"], values = [line_id])
            user_id = CallDatabase.get_data("users", ["id"], condition = user_condition, all_data = False)[0]
            init_condition = ["condition = 'initial'", f"user_id = {user_id}"]

        #在報名資訊資料庫創建一列，準備寫入使用者回答的資訊該列報名狀態為initial
        columns = ["activity_id", "condition", "user_id"]
        values = [activity_id, "initial", user_id]
        CallDatabase.insert("registration", columns = columns, values = values)
        
        registration_info = basic_info.basic_info(init_condition)[1]
        data_registration = user_info + registration_info
        
        msg = verify.next_msg("registration", data_registration, progress = 2)   #to-do 進度條待改
    return msg

def confirm_registration(activity_id, init_condition):
    condition = [f"id = {activity_id}"]
    people, activity_condition = CallDatabase.get_data("activity", ["people", "condition"], condition = condition, all_data = False)

    if activity_condition != "pending":
        msg = TextSendMessage(text = "報名失敗！")
        
    else:
        #將報名表單的condition改成closed
        CallDatabase.update("registration", columns = ["condition"], values = ["closed"], condition = init_condition)

        # 報名成功 重新取得報名人數
        condition = [f"activity_id = {activity_id}", f"condition = 'closed'"]
        count_attendee = len(CallDatabase.get_data("registration", condition = condition))

        #檢查報名人數attendee是否達上限people（上面有先從資料庫取出people了）
        #人數達上限則將活動狀態改為closed
        condition = [f"id = {activity_id}"]
        if count_attendee >= people:
            CallDatabase.update("activity", columns = ["condition"], values = ["closed"], condition = condition)

        #將更新的報名人數attendee記錄到報名表單group_data裡
        CallDatabase.update("activity", columns = ["attendee"], values = [count_attendee], condition = condition)
                
        # 回應 報名成功
        msg = TextSendMessage(text = "報名成功！")
    return msg    

def cancel_registration(registration_id, activity_id):
    # 從報名資訊資料庫中，將該報名紀錄的 condition 改為 delete
    condition = [f"id = {registration_id}"]
    CallDatabase.update("registration", columns = ["condition"], values = ["delete"], condition = condition)

    # 更新活動資訊資料庫中，該活動已報名人數
    condition = [f"activity_id = {activity_id}", f"condition = 'closed'"]
    count_attendee = len(CallDatabase.get_data("registration", condition = condition))
    condition = [f"id = {activity_id}"]
    CallDatabase.update("activity", columns = ["attendee"], values = [count_attendee], condition = condition)

    # 若該團的活動狀態為closed，則更新為pending
    activity_condition = CallDatabase.get_data("activity", ["condition"], condition = condition, all_data = False)[0]
    if activity_condition == "closed":
        CallDatabase.update("activity", columns = ["condition"], values = ["pending"], condition = condition)

    # 回應 取消成功
    msg = TextSendMessage(text = "取消成功！")        
    return msg
    