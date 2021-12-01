from models import CallDatabase
from templates import flexmsg_activity
import json

activity_columns = flexmsg_activity.columns
user_columns = ["name", "phone"]

def line_id(request_data):
    try:
        line_id = json.loads(request_data)["events"][0]["source"]["userId"]
    except:
        line_id = None
    return line_id 

def user_id(user_condition):
    user_id = CallDatabase.get_data("users", ["id"], condition = user_condition, all_data = False)
    user_id = user_id[0] if user_id else None
    return user_id

def basic_info(init_condition):
    activity_info = CallDatabase.get_data("activity", activity_columns[:-2], condition = init_condition, all_data = False)
    registration_info = CallDatabase.get_data("registration", ["activity_id", "id"], condition = init_condition, all_data = False)
    return activity_info, registration_info

def user_info(user_condition):
    user_info = CallDatabase.get_data("users", user_columns, condition = user_condition, all_data = False)
    return user_info
    