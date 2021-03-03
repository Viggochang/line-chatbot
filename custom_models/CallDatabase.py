# -*- coding: utf-8 -*-
import os
import psycopg2

def get_all_data():
    print("連接資料庫")
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    #cols = ("activity_type", "activity_name", "activity_date", "activity_time", "cost")
    select_query = '''SELECT activity_type, photo, activity_name, location_tittle, activity_date, activity_time, cost FROM group_data ORDER BY activity_date'''
    cursor.execute(select_query)
    conn.commit()
    
    all_data = [list(row) for row in cursor.fetchall()]
    default_photo = "https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip11.jpg"
    for row in all_data:
        if "https://i.imgur.com/" not in row[1] and "png" not in row[1]:
            row[1] = default_photo
    
    all_data = [all_data[i:i+4] for i in range(len(all_data)) if i%4 == 0]
    return all_data

def filter_group(form):
    print("連接資料庫")
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    activity_type, cost_min, cost_max = form["activity_type"], form["cost_min"], form["cost_max"]
    condition_query = []
    if activity_type:
        condition_query.append(f"activity_type = '{activity_type}'")
    if cost_min:
        condition_query.append(f"cost >= {cost_min}")
    if cost_max:
        condition_query.append(f"cost <= {cost_max}")
    
    if condition_query:
        select_query = '''SELECT activity_type, photo, activity_name, location_tittle, activity_date, activity_time, cost FROM group_data''' + ''' WHERE ''' + ''' AND '''.join(condition_query) + ''' ORDER BY activity_date'''
    else:
        select_query = '''SELECT activity_type, photo, activity_name, location_tittle, activity_date, activity_time, cost FROM group_data ORDER BY activity_date'''
    
    cursor.execute(select_query)
    conn.commit()
    
    filter_data = [list(row) for row in cursor.fetchall()]
    default_photo = "https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip11.jpg"
    for row in filter_data:
        if "https://i.imgur.com/" not in row[1]:
            row[1] = default_photo
            
    filter_data = [filter_data[i:i+4] for i in range(len(filter_data)) if i%4 == 0]
    return filter_data
