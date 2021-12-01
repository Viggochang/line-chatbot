from models import CallDatabase

def reset(user_id):
    if user_id:
        init_condition = ["condition = 'initial'", f"user_id = '{user_id}'"]

        CallDatabase.delete("activity", condition = init_condition)       # 刪除開團表單中未完成的資料
        CallDatabase.delete("registration", condition = init_condition)   # 刪除報名表單中未完成的資料
    
        print("刪除未成功資料")
