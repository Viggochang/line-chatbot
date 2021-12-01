import os
from models import CallDatabase
from imgurpython import ImgurClient

def photo(photo_content, imgur_config, activity_info, init_condition, user_id):
    if activity_info and None in activity_info and activity_info.index(None) == 11:
        activity_name = activity_info[1]
        #把圖片存下來並傳上去
        file_path = f"tmp/{user_id}_{activity_name}.png"
        with open(file_path, "wb") as tf:
            for chunk in photo_content.iter_content():
                tf.write(chunk)
            dist_path = tf.name

        print(f"dist_path = {dist_path}")

        try:
            client_id, client_secret, access_token, refresh_token, album_id = imgur_config
            client = ImgurClient( client_id, client_secret, access_token, refresh_token)
            con = {
                'album': album_id,
                'name': f'{user_id} / {activity_name}',
                'title': f'{user_id} / {activity_name}',
                'description': f'{user_id} / {activity_name}'
            }

            image = client.upload_from_path(dist_path, config = con, anon = False)
            os.remove(dist_path)
            #把圖片網址存進資料庫
            CallDatabase.update("activity", columns = ["photo"], values = [image['link']], condition = init_condition)
            print(image['link'])

            msg = "上傳成功！"

        except:
            CallDatabase.update("activity", columns = ["photo"], values = ["無"], condition = init_condition)
            msg = "上傳失敗！"

    else:
        msg = "現在不用傳圖片給我!"

    return msg    
    