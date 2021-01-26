# -*- coding: utf-8 -*-

from linebot.models import TextSendMessage

def cancel(line_bot_api, cursor, conn, event):

    postgres_select_query=f'''SELECT * FROM group_data WHERE user_id = '{event.source.user_id}' AND condition= 'initial';'''
    cursor.execute(postgres_select_query)
    data = cursor.fetchone()

    postgres_select_query=f'''SELECT * FROM registration_data WHERE user_id = '{event.source.user_id}' AND condition= 'initial';'''
    cursor.execute(postgres_select_query)
    data_2 = cursor.fetchone()

    postgres_delete_query = f"""DELETE FROM group_data WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
    cursor.execute(postgres_delete_query)
    conn.commit()
    postgres_delete_query = f"""DELETE FROM registration_data WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
    cursor.execute(postgres_delete_query)
    conn.commit()
    
    cursor.close()
    conn.close()
    
    if data or data_2:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "取消成功")
        )
        print("取消成功")
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "無可取消的開團/報名資料")
        )
        print("無可取消的開團/報名資料")


def reset(cursor, conn, event):
    #把只創建卻沒有寫入資料的列刪除
    postgres_delete_query = f"""DELETE FROM group_data WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
    cursor.execute(postgres_delete_query)
    conn.commit()
    postgres_delete_query = f"""DELETE FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
    cursor.execute(postgres_delete_query)
    conn.commit()
    print("刪除未成功資料")

