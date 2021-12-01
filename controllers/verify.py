from models import CallDatabase
from templates import flexmsg_activity, flexmsg_registration, flexmsg_question

activity_columns = flexmsg_activity.columns
user_columns = ["name", "phone"]

# 驗證是否回答完畢，判斷要問下一題或summary
def next_msg(status, data, progress = 0):
    print("進入verify.next_msg")
    if None in data: # 還有欄位未填，問下一題
        i = data.index(None)
        if "activity" in status:
            col = activity_columns[i]
            activity_date = data[2]
            msg = flexmsg_question.question(col, progress, activity_date)
        else:
            col = user_columns[i] 
            msg = flexmsg_question.question(col, progress)
        print("問下一題")
            
    else: # 所有欄位都填了，回傳summary
        if "activity" in status:
            msg = flexmsg_activity.summary(data)  
        else:
            activity_id = data[2]
            activity_name = CallDatabase.get_data("activity", ["activity_name"], condition = [f"id = {activity_id}"], all_data = False)[0]
            msg = flexmsg_registration.summary(data, activity_name)

    return msg

# 驗證使用者報名是否重複
def duplicate_registration(activity_id, user_id):
    condition = [f"activity_id = {activity_id}", "condition = 'closed'"]
    attendee_user_id = CallDatabase.get_data("registration", ["user_id"], condition = condition)
    attendee_user_id = [data[0] for data in attendee_user_id]

    return user_id in attendee_user_id #如果使用者輸入的電話重複則報名失敗
