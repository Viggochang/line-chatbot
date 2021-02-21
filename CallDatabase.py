# -*- coding: utf-8 -*-
import os
import psycopg2

def get_group_data():
    print("連接資料庫")
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    select_query = '''SELECT * FROM group_data ORDER BY activity_no'''
    cursor.execute(select_query)
    conn.commit()
    
    all_data = cursor.fetchall()
    return all_data
