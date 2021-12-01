from models import CallDatabase
from templates import flexmsg_question

def edit(table, column, init_condition, user_condition, activity_info):
    activity_date = activity_info[2] if activity_info else None
    condition = init_condition if table == "activity" else user_condition
    # 將資料庫中該題的內容清除
    CallDatabase.update(table, columns = [column], values = ["Null"], condition = condition)
    msg = flexmsg_question.question(column, progress = 0, activity_date = activity_date)
    return msg
    