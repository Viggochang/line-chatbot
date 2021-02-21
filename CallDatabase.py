# -*- coding: utf-8 -*-
import os
import psycopg2

def get_group_data():
    print("連接資料庫")
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    cols = ("activity_type", "activity_name", "activity_date", "activity_time", "cost")
    select_query = f'''SELECT {cols} FROM group_data ORDER BY activity_no'''
    cursor.execute(select_query)
    conn.commit()
    
    all_data = cursor.fetchall()
    return all_data
