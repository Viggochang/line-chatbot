# -*- coding: utf-8 -*-
import os
import psycopg2

def get_group_data():
    print("連接資料庫")
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    #cols = ("activity_type", "activity_name", "activity_date", "activity_time", "cost")
    select_query = '''SELECT activity_type, activity_name, activity_date, activity_time, cost FROM group_data ORDER BY activity_no'''
    cursor.execute(select_query)
    conn.commit()
    
    all_data = cursor.fetchall()
    return all_data

def filter_group(form):
    print("連接資料庫")
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    activity_type = form["activity_type"]
    cost_min = form["cost_min"]
    cost_max = form["cost_max"]
    
    select_query = f'''SELECT activity_type, activity_name, activity_date, activity_time, cost FROM group_data WHERE activity_type = {activity_type} AND cost >= cost_min AND cost <= cost_max'''
    
    cursor.execute(select_query)
    conn.commit()
    
    filter_data = cursor.fetchall()
    return filter_data
