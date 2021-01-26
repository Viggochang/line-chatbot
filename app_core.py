from __future__ import unicode_literals
import os
import configparser
import psycopg2
import datetime as dt
import tempfile
from imgurpython import ImgurClient

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
# from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, PostbackEvent, LocationMessage, ImageMessage

import flexmsg_g, flexmsg_r, flexmsg_glist, flexmsg_rlist
import cancel

app = Flask(__name__)

# LINE ��Ѿ����H���򥻸��
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp') # �s�Ϥ���

# ���� LINE ����T
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    print(f"body:{body}")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# �ǧA����
@handler.add(MessageEvent, message = TextMessage)
def app_core(event):
    progress_list_fullgroupdata=[7, 1, 2, 3, 4, 5, 6 ,7 ]
    progress_list_halfgroupdata=[5, 1, 2, 3, 4, 5]
    progress_list_fullregistrationdata=[2, 0, 0, 0, 0, 0, 1, 2]
    
#    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
#        line_bot_api.reply_message(
#        event.reply_token,
#        TextSendMessage(text=event.message.text)
#        )
    print(f"event:{event}")
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    print("�s����Ʈw")

    if event.message.text == "~cancel":
        cancel.cancel(line_bot_api, cursor, conn, event)

    # �}�l�^�����D�y�{
    else:
        postgres_select_query = f"""SELECT * FROM group_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
        cursor.execute(postgres_select_query)
        data_g = cursor.fetchone()
        print(f"data_g:{data_g}")
        column_all = ['acrivity_no', 'activity_type', 'activity_name',
                      'activity_date', 'activity_time', 'location_tittle', 'lat', 'long', 'people', 'cost',
                      'due_date', 'description', 'photo', 'name',
                      'phone', 'mail', 'attendee', 'condition', 'user_id']
    
        postgres_select_query = f"""SELECT * FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
        cursor.execute(postgres_select_query)
        #�ǳƼg�J���W��ƪ����@�C
        data_r = cursor.fetchone()
        print(f"data_r:{data_r}")
        column_all_registration = ['registration_no', 'activity_no',
                                   'activity_name', 'attendee_name', 'phone',
                                   'mail', 'condition', 'user_id']
        
## ================
## �ڭn�}��
## ================
        if data_g:
            progress_target = progress_list_fullgroupdata
            i = data_g.index(None) # �g�J��ƪ����@��
            
            if None in data_g:
                record = event.message.text
                #�p�G�ϥΪ̿�J����Ƥ��ŦX��Ʈw����ƫ��A, �h�^�� �Э��s��J
                try:
                    #��J���
                    postgres_update_query = f"""UPDATE group_data SET {column_all[i]} = '{record}' WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                    cursor.execute(postgres_update_query)
                    conn.commit()
                    
                except:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text = "�Э��s��J")
                    )
                
                #�p�G�٨S��J��̫�@��, �h�~��߰ݤU�@�D
                postgres_select_query = f"""SELECT * FROM group_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                cursor.execute(postgres_select_query)
                data_g = cursor.fetchone()
                print(f"��J��ƫ� data_g:{data_g}")
                
                if data_g[14]:
                    progress_target = progress_list_halfgroupdata

                if None in data_g: # �ݤU�@�D
                    i = data_g.index(None)
                    print(f"i={i}")
                                    
                    msg = flexmsg_g.flex(i, data_g, progress_target)
                    line_bot_api.reply_message(
                        event.reply_token,
                        msg)
                    print("�ݤU�@�D")
                        
                elif None not in data_g: # summarys

                    msg = flexmsg_g.summary(data_g)
                    line_bot_api.reply_message(
                        event.reply_token,
                        msg
                    )
                        

## ================
## �ڭn���W
## ================
        elif data_r:
        
            if None in data_r:
                   
                i_r = data_r.index(None)
                record = event.message.text

                postgres_select_query = f"""SELECT activity_no FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                cursor.execute(postgres_select_query)
                activity_no = cursor.fetchone()[0] #���o���b���W�����ʽs��

                postgres_select_query = f"""SELECT phone FROM registration_data WHERE activity_no = '{activity_no}';"""
                cursor.execute(postgres_select_query)
                phone_registration = cursor.fetchall() #���o���W�ӹΪ��q�ܦC��
                        
                    #��i����J�q�ܮ�(i_r==4)�A�}�l����O�_����
                if i_r == 4 and record in phone_registration[0]:
                    #�p�G�ϥΪ̿�J���q�ܭ��ƫh���W���ѡA�R���쥻�Ыت��C
                    postgres_delete_query = f"""DELETE FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                    cursor.execute(postgres_delete_query)
                    conn.commit()

                    line_bot_api.reply_message(
                        event.reply_token,
                        [TextSendMessage(text = "���i���Ƴ��W �Э��s��ܷQ�n���W����������"), flexmsg_r.activity_type_for_attendee]
                    )
                    #~~~�o��Pı�i�H�]�p�@��flex_msg�A�X�{[��^]���s�A���s�^����W�Ĥ@�B(���s�^��~join)

                else:
                    try:
                        # ��J��ƫ��A���T�h��s
                        postgres_update_query = f"""UPDATE registration_data SET {column_all_registration[i_r]} = '{record}' WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                        cursor.execute(postgres_update_query)
                        conn.commit()
       
                    except:
                        # ��J��ƫ��A���~�h�^�� "�Э��s��J"
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text = "�Э��s��J")
                        )

                # �ˬd�O�_�����Ҧ����D
                postgres_select_query = f"""SELECT * FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                cursor.execute(postgres_select_query)
                data_r = cursor.fetchone() #�ǳƼg�J���W��ƪ����@�C
                print("i_r = ",i_r)
                print("data_r = ",data_r)


                if None in data_r:
                
                    i_r = data_r.index(None)
                    msg = flexmsg_r.flex(i_r, progress_list_fullregistrationdata) #flexmsg�ݭn�s�W���W����
                    line_bot_api.reply_message(
                        event.reply_token,
                        msg
                    )
                    print("�ݤU�@�D")
                    
                #�X�{summary
                elif None not in data_r:
                    msg = flexmsg_r.summary_for_attend(data_r)
                    line_bot_api.reply_message(
                        event.reply_token,
                        msg
                    )
    
#�B�zpostback �ƥ�A�Ҧpdatetime picker
@handler.add(PostbackEvent)
def gathering(event):
    progress_list_fullgroupdata=[7, 1, 2, 3, 4, 5, 6 ,7]
    progress_list_halfgroupdata=[5, 1, 2, 3, 4, 5]
    progress_target = progress_list_fullgroupdata
    progress_list_fullregistrationdata=[2, 0, 0, 0, 0, 0, 1, 2]

    print(f"postback_event:{event}")
    
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    postgres_select_query = f"""SELECT * FROM group_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
    cursor.execute(postgres_select_query)
    data_g = cursor.fetchone()
    
    postback_data = event.postback.data
    
    if postback_data == "~cancel":
        cancel.cancel(line_bot_api, cursor, conn, event)
        
## ================
## �ڭn�}��
## ================
    elif postback_data == "�ڭn�}��":
        line_bot_api.reply_message(
            event.reply_token,
            flexmsg_g.activity_type
        )
        print("�ǳƶ}��")

        #��u�Ыثo�S���g�J��ƪ��C�R��
        cancel.reset(cursor, conn, event)
        
    elif "�}�ά�������" in postback_data:
        #��u�Ыثo�S���g�J��ƪ��C�R��
        cancel.reset(cursor, conn, event)
        
        type = postback_data.split("_")[1]
        print(f"type:{type}")

        #�Ыؤ@�C(condition = initial)
        postgres_insert_query = f"""INSERT INTO group_data (condition, user_id, activity_type, attendee, photo, description) VALUES ('initial', '{event.source.user_id}', '{type}', '1', '�L', '�L');"""
        cursor.execute(postgres_insert_query)
        conn.commit()
        
        #���D�������
        postgres_select_query = f'''SELECT name,phone FROM group_data WHERE user_id='{event.source.user_id}' AND condition != 'initial' ORDER BY activity_no DESC;'''
        cursor.execute(postgres_select_query)
        data_for_basicinfo = cursor.fetchone()

        if data_for_basicinfo:
            postgres_update_query = f"""UPDATE group_data SET name='{data_for_basicinfo[0]}' , phone='{data_for_basicinfo[1]}' WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
            cursor.execute(postgres_update_query)
            conn.commit()
            progress_target = progress_list_halfgroupdata

        cursor.close()
        conn.close()
        
        msg = flexmsg_g.flex(2, data=None, progress=progress_target)
        line_bot_api.reply_message(
            event.reply_token,
            msg
        )
        
    elif "�ק�}��" in postback_data:
        # �bsummary�I��ק��
        column = postback_data.split("_", 1)[1]

        postgres_update_query = f"""UPDATE group_data SET {column} = Null WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
        cursor.execute(postgres_update_query)
        conn.commit()
        
        progress_target = [7, 6, 6, 6, 6, 6, 6, 6]
        msg = flexmsg_g.flex(column, data_g, progress_target)
        line_bot_api.reply_message(
            event.reply_token,
            msg
        )
        
    elif "�T�{�}��" in postback_data:

        postgres_update_query = f"""UPDATE group_data SET condition = 'pending' WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
        cursor.execute(postgres_update_query)
        conn.commit()

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "�}�Φ��\�I")
        )

        cursor.close()
        conn.close()

        
## ================
## �ڭn���W
## ================
    elif postback_data == "�ڭn���W":
        line_bot_api.reply_message(
            event.reply_token,
            flexmsg_r.activity_type_for_attendee
        )
        print("�ǳƥi���W�θ�T")
        
        #��u�Ыثo�S���g�J��ƪ��C�R��
        cancel.reset(cursor, conn, event)
        
    # ���Urich menu��"�ڭn���W" ��ܨ䤤�@�ج���������
    elif "���W��������" in postback_data: #�o�̪�event.message.text�|�O�W��quick reply�^�Ǫ��T��(�|��type�䤤�@��)
        type = postback_data.split("_")[1]

        postgres_select_query = f"""SELECT * FROM group_data WHERE activity_date >= '{dt.date.today()}' AND activity_type = '{type}'  and people > attendee and condition = 'pending' ORDER BY activity_date ASC ;"""
        cursor.execute(postgres_select_query)
        data_carousel = cursor.fetchall()

        msg = flexmsg_r.carousel(data_carousel, type)
        line_bot_api.reply_message(
            event.reply_token,
            msg
        )

    elif "�ԲӸ�T" in postback_data :
        record = postback_data.split("_")
        
        postgres_select_query = f"""SELECT * FROM group_data WHERE activity_no = '{record[0]}' ;"""
        cursor.execute(postgres_select_query)
        data_tmp = cursor.fetchone()
        msg = flexmsg_r.MoreInfoSummary(data_tmp)

        line_bot_api.reply_message(
            event.reply_token,
            msg
        )

    elif "�ߧY���W" in postback_data: #�I�F"�ߧY���W��Y�^��activity_no�Mactivity_name"
        record = postback_data.split("_")
        #record[0]:�ߧY���W record[1]�G���ʥN�� record[2]:���ʦW��

        #��u�Ыثo�S���g�J��ƪ��C�R��
        cancel.reset(cursor, conn, event)

        #�Ыؤ@�C
        postgres_insert_query = f"""INSERT INTO registration_data (condition, user_id, activity_no, activity_name, activity_date) VALUES ('initial', '{event.source.user_id}','{record[1]}', '{record[2]}', '{record[3]}');"""
        cursor.execute(postgres_insert_query)
        conn.commit()

        #�����Ϊ̪����
        postgres_select_query = f'''SELECT attendee_name, phone FROM registration_data WHERE user_id = '{event.source.user_id}' and condition != 'initial' ORDER BY registration_no DESC;'''
        cursor.execute(postgres_select_query)
        data_for_basicinfo = cursor.fetchone()
        print("data_for_basicinfo = ", data_for_basicinfo)

        #�f�ֹq��
        postgres_select_query = f"""SELECT phone FROM registration_data WHERE activity_no = '{record[1]}' ;"""
        cursor.execute(postgres_select_query)
        phone_registration = [data[0] for data in cursor.fetchall() if data[0] != None]

        print(f"phone_registration:{phone_registration}")
        
        if data_for_basicinfo:
            name = data_for_basicinfo[0]
            phone = data_for_basicinfo[1]
        else:
            name, phone = None, None
        
        if name != None and phone != None and phone not in phone_registration:
            # �w�����W�����h�����a�J���e���
            postgres_update_query = f"""UPDATE registration_data SET attendee_name='{data_for_basicinfo[0]}' , phone='{data_for_basicinfo[1]}' WHERE (condition, user_id) = ('initial', '{event.source.user_id}');"""
            cursor.execute(postgres_update_query)
            conn.commit()
            postgres_select_query = f"""SELECT * FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
            cursor.execute(postgres_select_query)
            
            data_r = cursor.fetchone()
            msg = flexmsg_r.summary_for_attend(data_r)
            line_bot_api.reply_message(
                event.reply_token,
                msg
            )
    
        else:
            # ���s��g���W���
            postgres_select_query = f"""SELECT * FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
            cursor.execute(postgres_select_query)
            
            data_r = cursor.fetchone()
            i_r = data_r.index(None)
            print(f"count none in data_r = {data_r.count(None)}")
            print(f"i_r = {i_r}")
        
            msg = flexmsg_r.flex(i_r, progress_list_fullregistrationdata) #flexmsg�ݭn�s�W���W����
            line_bot_api.reply_message(
                event.reply_token,
                msg
            )
            
    elif "�ק���W" in postback_data:
        column = postback_data.split("_", 1)[1]  # attendee_name �� phone

        postgres_update_query = f"""UPDATE registration_data SET {column} = Null WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
        cursor.execute(postgres_update_query)
        conn.commit()
        
        msg = flexmsg_r.flex(column, [2, 0, 0, 0, 0, 0, 1, 1])
        line_bot_api.reply_message(
            event.reply_token,
            msg
        )

        
    elif "�T�{���W" in postback_data:
        #���L�����Ϊ��s��activity_no
        postgres_select_query = f"""SELECT activity_no FROM registration_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
        cursor.execute(postgres_select_query)
        activity_no = cursor.fetchone()[0]

        #����ӹβ{�b�����W�H��attendee�ç�s(+1)
        postgres_select_query = f"""SELECT attendee, condition FROM group_data WHERE activity_no = {activity_no};"""
        cursor.execute(postgres_select_query)
        temp = cursor.fetchone()
        attendee = temp[0]
        condition = temp[1]
        if condition == "closed":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text = "���W����")
            )
            
        else:
            attendee += 1

            #�N��s�����W�H��attendee�O������W���group_data��
            postgres_update_query = f"""UPDATE group_data SET attendee = {attendee} WHERE activity_no = {activity_no};"""
            cursor.execute(postgres_update_query)
            conn.commit()

            #�ˬd���W�H��attendee�O�_�F�W��people
            postgres_select_query = f"""SELECT people FROM group_data WHERE activity_no = {activity_no};"""
            cursor.execute(postgres_select_query)
            people = cursor.fetchone()[0]

            if attendee == people:
                postgres_update_query = f"""UPDATE group_data SET condition = 'closed' WHERE activity_no = {activity_no};"""
                cursor.execute(postgres_update_query)
                conn.commit()


            #�N���W��檺condition�令closed
            postgres_update_query = f"""UPDATE registration_data SET condition = 'closed' WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
            cursor.execute(postgres_update_query)
            conn.commit()

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text = "���W���\�I")
            )

            cursor.close()
            conn.close()


## ================
## �ڪ��}��
## ================
    elif postback_data == "�ڪ��}��":
        line_bot_api.reply_message(
            event.reply_token,
            flexmsg_glist.list_type
        )
        print("�d�߶}�ά���")
        
    elif "�}�ά���" in postback_data:
        
        type = postback_data.split("_")[1]
        
        if type == "�w����":
            postgres_select_query = f"""SELECT * FROM group_data WHERE user_id = '{event.source.user_id}' AND activity_date < '{dt.date.today()}' AND condition != 'initial' ORDER BY activity_date ASC;"""
        elif type == "�i�椤":
            postgres_select_query = f"""SELECT * FROM group_data WHERE user_id = '{event.source.user_id}' AND activity_date >= '{dt.date.today()}' AND condition != 'initial' ORDER BY activity_date ASC;"""
            
        cursor.execute(postgres_select_query)
        group_data = cursor.fetchall()
        print(f"group_data:{group_data}")

        msg = flexmsg_glist.glist(group_data, type)
        line_bot_api.reply_message(
        event.reply_token,
        msg
        )
        
    elif "�}�θ�T" in postback_data:
        activity_no = postback_data.split("_")[1]
        postgres_select_query = f"""SELECT * FROM group_data WHERE activity_no = '{activity_no}';"""
        cursor.execute(postgres_select_query)
        group_data = cursor.fetchone()
        print("group_data = ", group_data)
        
        msg = flexmsg_glist.MyGroupInfo(group_data)
        line_bot_api.reply_message(
            event.reply_token,
            msg
            )
            
    #�D���d�ݳ��W�̸�T(���W�̼ʺ١B�q��)
    elif "���W�̸�T" in postback_data:
        activity_no = postback_data.split("_")[1]

        postgres_select_query = f"""SELECT activity_name FROM registration_data WHERE activity_no = '{activity_no}';"""
        cursor.execute(postgres_select_query)

#         try:
        temp = cursor.fetchone()
        if temp:
            activity_name = "".join(temp)
            print("activity_name = ", activity_name)

            postgres_select_query = f"""SELECT attendee_name, phone FROM registration_data WHERE activity_no = '{activity_no}' ;"""
            cursor.execute(postgres_select_query)
            attendee_data = cursor.fetchall()
            print("attendee_data = ", attendee_data)

            attendee_lst = []
            for row in attendee_data:
                attendee_lst.append(" ".join(row))

            msg = f"{activity_name}"+"\n���W�̸�T�G"
            for attendee in attendee_lst:
                msg += f"\n{attendee}"
    #         except:
    #             msg = "�����ʥثe�L�H���W"

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text = msg)
                )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text = '�ثe�L�H���W')
                )
    #�D����������
    elif "�������W" in postback_data:
        activity_no = postback_data.split("_")[1]
        
        postgres_update_query = f"""UPDATE group_data SET condition = 'closed' WHERE activity_no = '{activity_no}';"""
        cursor.execute(postgres_update_query)
        conn.commit()

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "���\�������W�I")
            )
       
## ================
## �ڪ����W
## ================
    elif postback_data == "�ڪ����W":
        line_bot_api.reply_message(
            event.reply_token,
            flexmsg_rlist.list_type
        )
        print("�d�߳��W����")
        
    elif "���W����" in postback_data:
    
        type = postback_data.split("_")[1]
        
        if type == "�w����":
            postgres_select_query = f"""SELECT activity_no, activity_name, activity_date FROM registration_data WHERE user_id = '{event.source.user_id}' AND activity_date < '{dt.date.today()}' AND condition != 'initial' ORDER BY activity_date ASC;;"""
 
        elif type == "�i�椤":
            postgres_select_query = f"""SELECT activity_no, activity_name, activity_date FROM registration_data WHERE user_id = '{event.source.user_id}' AND activity_date >= '{dt.date.today()}' AND condition != 'initial' ORDER BY activity_date ASC;;"""
            
        cursor.execute(postgres_select_query)
        rg_data = sorted(list(set(cursor.fetchall())), key = lambda x: x[2])
        print(f"rg_data:{rg_data}")

        msg = flexmsg_rlist.rlist(rg_data, type)
        line_bot_api.reply_message(
        event.reply_token,
        msg
        )
    
    # �b���W�C���I�ﬡ��
    elif "�d���W" in postback_data:
        activity_no = postback_data.split('_')[0]
        
        #�ھڦ^�Ǫ�activity_no�A�qgroup_data�̧�쬡�ʸ�T
        postgres_select_query = f"""SELECT * FROM group_data WHERE activity_no = {activity_no};"""
        cursor.execute(postgres_select_query)
        group_info = cursor.fetchone()
        #�ھڦ^�Ǫ�activity_no�Muser_id�����W��T(�i�ण�u�@�C)
        postgres_select_query = f"""SELECT * FROM registration_data WHERE activity_no = {activity_no} AND user_id = '{event.source.user_id}';"""
        cursor.execute(postgres_select_query)
        registration_info = cursor.fetchall()
        
        msg = flexmsg_rlist.carousel_registration(group_info, registration_info)
        line_bot_api.reply_message(
            event.reply_token,
            msg
        )
        
    elif "�������W" in postback_data: #���U�������W���s�N�^��(record_activity_�������W)
        registration_no = postback_data.split('_')[0]
        activity_no = postback_data.split('_')[1]

        # �R�����W
        postgres_delete_query = f"""DELETE FROM registration_data WHERE registration_no = {registration_no} AND user_id = '{event.source.user_id}';"""
        cursor.execute(postgres_delete_query)
        conn.commit()

        #����ӹβ{�b�����W�H��attendee�ç�s(-1)
        postgres_select_query = f"""SELECT attendee FROM group_data WHERE activity_no = {activity_no};"""
        cursor.execute(postgres_select_query)
        attendee = cursor.fetchone()[0]
        attendee -= 1

        #�N��s�����W�H��attendent�O������W���group_data��
        postgres_update_query = f"""UPDATE group_data SET attendee = {attendee} WHERE activity_no = {activity_no};"""
        cursor.execute(postgres_update_query)
        conn.commit()

        #��s�Ӭ��ʪ�condition(=pending)
        postgres_update_query = f"""UPDATE group_data SET condition = 'pending' WHERE activity_no = {activity_no};"""
        cursor.execute(postgres_update_query)
        conn.commit()

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "�������\�I")
        )

## ================
## �W�U��
## ================
    elif "forward" in postback_data or "backward" in postback_data:
        
        record = postback_data.split("_") #record[0] = forward, reocord[1] = command
        type = record[2]
        i = int(record[3])

        # [�ڭn���W] ���ʦC���U�@��
        if record[1] == "activity":
            #record[2] = activity_type, record[3] = i
            postgres_select_query = f"""SELECT * FROM group_data WHERE activity_date >= '{dt.date.today()}' AND activity_type = '{record[2]}' and people > attendee and condition = 'pending' ORDER BY activity_date ASC;"""
           
            cursor.execute(postgres_select_query)
            data = cursor.fetchall()
            print(f"data:{data}")
            msg = flexmsg_r.carousel(data, type, i)
            
        # [�ڪ��}��] �}�ΦC���U�@��
        elif record[1] == "glist":
            #record[2] = �i�椤�Τw����, record[3] = i
            if type == "�w����":
                postgres_select_query = f"""SELECT * FROM group_data WHERE user_id = '{event.source.user_id}' AND activity_date < '{dt.date.today()}' ORDER BY activity_date ASC;"""
            elif type == "�i�椤":
                postgres_select_query = f"""SELECT * FROM group_data WHERE user_id = '{event.source.user_id}' AND activity_date >= '{dt.date.today()}' ORDER BY activity_date ASC;"""
           
            cursor.execute(postgres_select_query)
            data = cursor.fetchall()
            print(f"data:{data}")
            msg = flexmsg_glist.glist(data, type, i)


        # [�ڪ����W] ���W�C���U�@��
        elif record[1] == "rlist":
            #record[2] = �i�椤�Τw����, record[3] = i
            if type == "�w����":
                postgres_select_query = f"""SELECT activity_no, activity_name, activity_date FROM registration_data WHERE user_id = '{event.source.user_id}' AND activity_date < '{dt.date.today()}' ORDER BY activity_date ASC;;"""
            elif type == "�i�椤":
                postgres_select_query = f"""SELECT activity_no, activity_name, activity_date FROM registration_data WHERE user_id = '{event.source.user_id}' AND activity_date >= '{dt.date.today()}' ORDER BY activity_date ASC;;"""
            
            cursor.execute(postgres_select_query)
            data = sorted(list(set(cursor.fetchall())), key = lambda x: x[2])
            print(f"data:{data}")
            msg = flexmsg_rlist.rlist(data, type, i)
        
        line_bot_api.reply_message(
            event.reply_token,
            msg
            )
                
## ================
## �}�Φ^�Ǯɶ�
## ================
    else:
        # �}�ή�,��g�ɶ����
        i = data_g.index(None)
        print("i =",i)
        column_all = ['acrivity_no', 'activity_type', 'activity_name',
                      'activity_date', 'activity_time', 'location_tittle', 'lat', 'long', 'people', 'cost',
                      'due_date', 'description', 'photo', 'name',
                      'phone', 'mail', 'attendee', 'condition', 'user_id']
        #�B�zactivity date and time
        if event.postback.data == "activity_time" :

            record = event.postback.params['datetime']
            record = record.split("T")
            print(record)
            temp = dt.datetime.strptime(record[0], "%Y-%m-%d") - dt.timedelta(days=1) #due_date
            # �g�J���(��s���ʤ���B�ɶ��A�w��I��ɶ��^
            postgres_update_query = f"""UPDATE group_data SET ({column_all[i]},{column_all[i+1]},{column_all[i+7]} ) = ('{record[0]}','{record[1]}','{temp}') WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
            cursor.execute(postgres_update_query)
            conn.commit()

            #�B�zdue date
        elif event.postback.data == "due_time":

            record = event.postback.params['date']
            # �g�J���(��s�I��ɶ�)
            postgres_update_query = f"""UPDATE group_data SET {column_all[i]} = '{record}' WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
            cursor.execute(postgres_update_query)
            conn.commit()

        #postgres_select_query = f"""SELECT * FROM group_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
        cursor.execute(postgres_select_query)
        data_g = cursor.fetchone()
        
        if data_g[14]:
            progress_target = progress_list_halfgroupdata
            
        if None in data_g:
            i = data_g.index(None)
            msg = flexmsg_g.flex(i, data_g, progress_target)
            line_bot_api.reply_message(
                event.reply_token,
                msg)
        elif None not in data_g:
            msg = flexmsg_g.summary(data_g)
            line_bot_api.reply_message(
                event.reply_token,
                msg)
                
        cursor.close()
        conn.close()
                

@handler.add(MessageEvent, message = LocationMessage)
def gathering(event):
    progress_list_fullgroupdata=[7, 1, 2, 3, 4, 5, 6 ,7 ]
    progress_list_halfgroupdata=[5, 1, 2, 3, 4, 5]
    progress_target = progress_list_fullgroupdata
    
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    postgres_select_query = f"""SELECT * FROM group_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
    cursor.execute(postgres_select_query)
    data_g = cursor.fetchone()
    
    i = data_g.index(None)
    print("i =",i)

    record = [event.message.title, event.message.latitude, event.message.longitude]
    if record[0] == None:
        record[0] = event.message.address[:50]
    # �g�J���(��s��m��T)
    postgres_update_query = f"""UPDATE group_data SET (location_tittle, lat, long) = ('{record[0]}', '{record[1]}', '{record[2]}') WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
    cursor.execute(postgres_update_query)
    conn.commit()
    
    cursor.execute(postgres_select_query)
    data_g = cursor.fetchone()
    
    if data_g[14]:
        progress_target = progress_list_halfgroupdata
    
    if None in data_g:
        i = data_g.index(None)
        msg = flexmsg_g.flex(i, data_g, progress_target)
        line_bot_api.reply_message(
            event.reply_token,
            msg)
    elif None not in data_g:
        msg = flexmsg_g.summary(data_g)
        line_bot_api.reply_message(
            event.reply_token,
            msg
        )
    cursor.close()
    conn.close()
    
@handler.add(MessageEvent, message = ImageMessage)
def handle_message(event):
    if isinstance(event.message, ImageMessage):
#         ext = 'jpg'
        print(event)
        print(event.message.id)
        
#        config = configparser.ConfigParser()
#        config.read('config.ini')
#        line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
        message_content = line_bot_api.get_message_content(event.message.id)
        
        with tempfile.NamedTemporaryFile(dir = static_tmp_path, prefix=ext + '-', delete=False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
            tempfile_path = tf.name

        dist_path = tempfile_path + '.' + ext
        dist_name = os.path.basename(dist_path)
        os.rename(tempfile_path, dist_path)
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            client = ImgurClient(config.get('imgur', 'client_id'), config.get('imgur', 'client_secret'), config.get('imgur', 'access_token'), config.get('imgur', 'refresh_token'))
            con = {
                'album': config.get('imgur', 'album_id'),
                'name': f'{event.source.user_id}_{data_g[3]}',
                'title': f'{event.source.user_id}_{data_g[3]}',
                'description': f'{event.source.user_id}_{data_g[3]}'
            }
            
            path = os.path.join('static', 'tmp', dist_name)
            client.upload_from_path(path, config=con, anon=False)
            os.remove(path)
            print(path)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='�W�Ǧ��\'))
        except:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='�W�ǥ���'))
        return 0


@handler.add(MessageEvent, message = ImageMessage)
def pic(event):
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode = 'require')
    cursor = conn.cursor()
    postgres_select_query = f"""SELECT * FROM group_data WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
    cursor.execute(postgres_select_query)
    data_g = cursor.fetchone()
    if data_g:
        i = data_g.index(None)
        print("i =",i)
        if i == 12:

            #��Ϥ��s�U�ӨöǤW�h
            ext = 'jpg'
            print(f"messege_id : {event.message.id}")
            print(event)
            message_content = line_bot_api.get_message_content(event.message.id)

            with tempfile.NamedTemporaryFile(dir = static_tmp_path, prefix = ext + '-', delete = False) as tf:
                for chunk in message_content.iter_content():
                    tf.write(chunk)
                tempfile_path = tf.name

            dist_path = tempfile_path + '.' + ext
            dist_name = os.path.basename(dist_path)
            os.rename(tempfile_path, dist_path)

            try:
                config = configparser.ConfigParser()
                config.read('config.ini')
                client = ImgurClient(config.get('imgur', 'client_id'), config.get('imgur', 'client_secret'), config.get('imgur', 'access_token'), config.get('imgur', 'refresh_token'))
                con = {
                    'album': config.get('imgur', 'album_id'),
                    'name': f'{event.source.user_id}_{data_g[3]}',
                    'title': f'{event.source.user_id}_{data_g[3]}',
                    'description': f'{event.source.user_id}_{data_g[3]}'
                }
                path = os.path.join('static', 'tmp', dist_name)
                image = client.upload_from_path(path, config=con, anon=False)
                print("path = ",path)
                os.remove(path)
                print("image = ",image)
                #��Ϥ����}�s�i��Ʈw
                postgres_update_query = f"""UPDATE group_data SET photo = '{image['link']}' WHERE condition = 'initial' AND user_id = '{event.source.user_id}';"""
                cursor.execute(postgres_update_query)
                conn.commit()

                msg=[TextSendMessage(text="�W�Ǧ��\"),
                     ImageSendMessage(original_content_url = image['link'], preview_image_url=image['link']),
                     TextSendMessage(text=request.host_url + os.path.join('static', 'tmp', dist_name)+"\n\n"+image['link'])]

                msg.append(flexmsg_g.summary(data_g))

                line_bot_api.reply_message(
                    event.reply_token,
                    msg
                )

            except:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='�W�ǥ���'))

    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "�{�b���ζǹϤ�����")
        )
    return 0


if __name__ == "__main__":
    app.run()
