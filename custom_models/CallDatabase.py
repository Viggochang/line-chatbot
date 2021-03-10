# -*- coding: utf-8 -*-
import os
import psycopg2
import datetime as dt

print("連接資料庫")
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

default_photo = "https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip11.jpg"

def get_group_data(table, condition = None, order = None, ASC = True, all_data = True):
    if condition:
        condition_query = "WHERE " + " AND" .join([f"{key} = '{condition[key]}'" for key in condition.keys()])
    if order:
        order_query = f" ORDER BY {order}" + (" ASC" if ASC else " DESC")
    postgres_select_query = f"""SELECT * FROM {table} """ + condition_query + order_query
    
    cursor.execute(postgres_select_query)
    conn.commit
    
    if all_data:
        all_data = [list(row) for row in cursor.fetchall()]
        if table == "group_data":
            for row in all_data:
                if "https://i.imgur.com/" not in row[12]:
                    row[12] = default_photo
        return all_data
        
    else:
        data = list(cursor.fetchone())
        if table == "group_data":
            if "https://i.imgur.com/" not in data[12]:
                data[12] = default_photo
        return data
    

def g_summary(user_id):
    postgres_select_query = f"""SELECT * FROM group_data WHERE condition = 'pending' AND user_id = '{user_id}' ORDER BY activity_no DESC;"""
    cursor.execute(postgres_select_query)
    conn.commit
    
    data = list(cursor.fetchone())
    if "https://i.imgur.com/" not in data[12]:
        data[12] = default_photo
    
    return data

    
def get_all_data():
    #cols = ("activity_type", "activity_name", "activity_date", "activity_time", "cost")
    select_query = f"""SELECT activity_type, photo, activity_name, location_tittle, activity_date, activity_time, cost, activity_no FROM group_data WHERE people > attendee AND condition = 'pending' AND activity_date > '{dt.date.today()}' ORDER BY activity_date;"""
    cursor.execute(select_query)
    conn.commit()
    
    all_data = [list(row) for row in cursor.fetchall()]

    for row in all_data:
        if "https://i.imgur.com/" not in row[1]:
            row[1] = default_photo
    
    all_data = [all_data[i:i+4] for i in range(len(all_data)) if i%4 == 0]
    return all_data

def filter_group(form):
    activity_type, cost_min, cost_max = form["activity_type"], form["cost_min"], form["cost_max"]
    condition_query = []
    if activity_type:
        condition_query.append(f"activity_type = '{activity_type}'")
    if cost_min:
        condition_query.append(f"cost >= {cost_min}")
    if cost_max:
        condition_query.append(f"cost <= {cost_max}")
    
    if condition_query:
        select_query = f'''SELECT activity_type, photo, activity_name, location_tittle, activity_date, activity_time, cost, activity_no FROM group_data WHERE ''' + ''' AND '''.join(condition_query) + ''' AND people > attendee AND condition = 'pending' AND activity_date > '{dt.date.today()}' ORDER BY activity_date;'''
    else:
        select_query = f"""SELECT activity_type, photo, activity_name, location_tittle, activity_date, activity_time, cost, activity_no FROM group_data WHERE people > attendee AND condition = 'pending' AND activity_date > '{dt.date.today()}' ORDER BY activity_date;"""
    
    cursor.execute(select_query)
    conn.commit()
    
    filter_data = [list(row) for row in cursor.fetchall()]

    for row in filter_data:
        if "https://i.imgur.com/" not in row[1]:
            row[1] = default_photo
            
    filter_data = [filter_data[i:i+4] for i in range(len(filter_data)) if i%4 == 0]
    return filter_data

def r_detail(activity_no):

    postgres_select_query = f"""SELECT * FROM group_data WHERE activity_no = {activity_no};"""
    cursor.execute(postgres_select_query)
    conn.commit
    
    data = list(cursor.fetchone())
    if "https://i.imgur.com/" not in data[12]:
        data[12] = default_photo
    
    return data

def r_summary(activity_no):

    postgres_select_query = f"""SELECT activity_type, photo, activity_name, location_tittle, activity_date, activity_time, cost, activity_no FROM group_data WHERE activity_no = {activity_no};"""
    cursor.execute(postgres_select_query)
    conn.commit
    
    data = list(cursor.fetchone())
    if "https://i.imgur.com/" not in data[1]:
        data[1] = default_photo
    
    return data

def attendee_data(activity_no):
    postgres_select_query = f"""SELECT attendee_name, phone FROM registration_data WHERE activity_no = {activity_no};"""
    cursor.execute(postgres_select_query)
    conn.commit
    
    data = cursor.fetchall()
    return data
