# -*- coding: utf-8 -*-
import os
import psycopg2

def get_all_data():
    print("連接資料庫")
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    #cols = ("activity_type", "activity_name", "activity_date", "activity_time", "cost")
    select_query = '''SELECT activity_type, activity_name, activity_date, activity_time, cost FROM group_data ORDER BY activity_data'''
    cursor.execute(select_query)
    conn.commit()
    
    all_data = cursor.fetchall()
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
        select_query = '''SELECT activity_type, activity_name, activity_date, activity_time, cost FROM group_data''' + ''' WHERE ''' + ''' AND '''.join(condition_query) + ''' ORDER BY activity_date'''
    else:
        select_query = '''SELECT activity_type, activity_name, activity_date, activity_time, cost FROM group_data ORDER BY activity_date'''
    
    cursor.execute(select_query)
    conn.commit()
    
    filter_data = cursor.fetchall()
    return filter_data
