# -*- coding: utf-8 -*-
import os
import psycopg2
import datetime as dt
now_timestamp = dt.datetime.now().timestamp()

# 連接資料庫
# DATABASE_URL = os.environ["DATABASE_URL"]
DATABASE_URL = "postgres://kfcgjdnbgqalif:503a165ffdfaed9dde93a0196045fe9db0ea2464206a1c129af5580932ccdab5@ec2-54-227-246-76.compute-1.amazonaws.com:5432/d107jas11a6r56"
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

def get_data(table, columns = "*", condition = None, order = None, ASC = True, all_data = True):

    default_photo = "https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip11.jpg"

    # 處理查詢欄位
    columns = ",".join(columns)
    # 處理篩選條件
    condition_query = "WHERE " + " AND ".join(condition) if condition else ""
    # 處理排序
    order_query = f" ORDER BY {order}" + (" ASC" if ASC else " DESC") if order else ""
        
    postgres_select_query = f"""SELECT {columns} FROM {table} {condition_query} {order_query}"""
    
    cursor.execute(postgres_select_query)
    conn.commit
    
    # 選取資料
    data = [list(row) for row in cursor.fetchall()] if all_data else cursor.fetchone() 
    return data
    
def insert(table, columns, values):

    columns.append("created_at")
    values.append(now_timestamp)

    columns = ",".join([f"{col}" for col in columns])
    values = ",".join([f"'{val}'" for val in values])
    postgres_insert_query = f"""INSERT INTO {table} ({columns}) VALUES ({values})"""
    
    cursor.execute(postgres_insert_query)
    conn.commit()
    
def update(table, columns, values, condition):

    columns = ",".join([f"{col}" for col in columns])
    values = ",".join([f"'{val}'" for val in values]) if values != ["Null"] else "Null"
    condition_query = "WHERE " + " AND ".join(condition)
    
    if "," not in columns:
        postgres_update_query = f"""UPDATE {table} SET {columns} = {values} {condition_query}"""
    else:
        postgres_update_query = f"""UPDATE {table} SET ({columns}) = ({values}) {condition_query}"""

    cursor.execute(postgres_update_query)
    conn.commit()

    time_query = f"""UPDATE {table} SET updated_at = {now_timestamp} {condition_query}"""
    cursor.execute(time_query)
    conn.commit()   
        
def delete(table, condition):

    condition_query = " WHERE " + " AND ".join(condition)
    postgres_delete_query = f"""DELETE FROM {table} {condition_query}"""
    
    cursor.execute(postgres_delete_query)
    conn.commit()
