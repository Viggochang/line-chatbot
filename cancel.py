
def cancel(cursor, conn, event):

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
        TextSendMessage(text='取消成功')
        )
    else:
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='無可取消的開團/報名資料')
        )
