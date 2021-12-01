from linebot.models import *

def quick_reply_button(status, label, record_type):
    quick_reply_button = QuickReplyButton(
        action = PostbackAction(
            label = label, 
            data = f"{status}紀錄_{record_type}",
            display_text = f"查詢[{label}]"
        )
    )
    return quick_reply_button

def record_type(status):
    all_label = [f"歷史{status}紀錄", "即將來臨的活動"]
    all_type = ["已結束", "進行中"]
    
    record_type = TextSendMessage(
        text = f"請選擇查詢 [歷史{status}紀錄] 或 [即將來臨的活動]",
        quick_reply = QuickReply(
            items = [quick_reply_button(status, label, record_type) for label, record_type in zip(all_label, all_type)]
        )
    )
    return record_type  
#------------------------------------------------------------------------------------------     
def activity_in_index(status, row):
    if status == "開團":
        activity_id, activity_name = row
    else:
        activity_id, registration_id, activity_name, activity_date = row    

    activity_in_index = BoxComponent(
        layout = "baseline",
        contents = [
            IconComponent(
                url =  "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png",
                size =  "sm"
            ),
            TextComponent(
                text = f"{activity_name}",  # activity_name
                align = "start",
                size = "md",
                color = "#227C9D",
                margin = "md",
                action = PostbackAction(
                    display_text = f"查看 {activity_name} 的詳細資訊",
                    data = f"開團資訊_{activity_id}" if status == "開團" else f"查報名_{activity_id}_{registration_id}"
                )
            )
        ]
    )
    return activity_in_index

def page_button(status, new_page, record_type, i):
    i = i-8 if new_page == "上一頁" else i+8
    page_button = ButtonComponent(
        action = PostbackAction(
            label = new_page,
            data = f"newPage_{record_type}_{i}_{status}紀錄",
            display_text = new_page
        ),
        height = "sm",
        style = "primary",
        color = "#A7D5E1",
        gravity = "bottom"
    )
    return page_button

def record_list(status, data, record_type, i = 0):

    if data:
        if i < 0:
            i = 0
        elif i >= len(data):
            i -= 8

        index_content = [activity_in_index(status, row) for row in data[i: i+8]]  
        index = BubbleContainer(
            size = "kilo",
            direction = "ltr",
            header = BoxComponent(
                layout = "horizontal",
                contents = [
                    TextComponent(
                        text = f"我的{status}列表 ({record_type})",
                        size = "lg",
                        weight = "bold",
                        color = "#AAAAAA"
                    )
                ]
            ),
            body = BoxComponent(
                layout = "vertical",
                spacing = "md",
                contents = index_content
            ),
            footer = BoxComponent(
                layout = "horizontal",
                spacing = "sm",
                contents = [
                    page_button(status, "上一頁", record_type, i),
                    page_button(status, "下一頁", record_type, i)
                ]
            )
        )
    else:
        index = BubbleContainer(
            direction = "ltr",
            body = BoxComponent(
                size = "xs",
                layout = "vertical",
                contents = [
                    TextComponent(
                        text = f"目前沒有{status}資料！",
                        size = "lg",
                        weight = "bold",
                        color = "#AAAAAA"
                    )
                ]
            )
        )

    record_list = FlexSendMessage(
        alt_text = f"我的{status}",
        contents = index
    )

    return record_list
#--------------------------------------------------------------------------------------
def climate(activity_no, activity_name):
    climate = BoxComponent(
        layout = "vertical",
        spacing = "sm",
        background_color = "#A7D5E1",
        width = "80px",
        height = "25.5px",                                           
        contents = [
            TextComponent(
                text = "天氣預報",
                size = "sm",
                color = "#FFFFFF",
                align = "center",
                offset_top = "2.5px"
            )
        ],
        action = PostbackAction(
            label = "天氣預報",
            data = f"climate_{activity_no}",
            display_text = f"{activity_name}的天氣預報"
        )
    )
    return climate

def info_text(text, color = "#8c8c8c", size = "xs", weight = "regular"):
    info_text = TextComponent(
        text = text,
        wrap = True,
        color = color,
        size = size,
        weight = weight
    ) 
    return info_text   

def button(label, data, display_text):
    button = ButtonComponent(
        style = "primary",
        height = "sm",
        color = "#A7D5E1",
        gravity = "bottom",
        action = PostbackAction(
            label = label,
            data = data,
            display_text = display_text
        )
    )
    return button   

def activity_info(data, owner_info = None):
    activity_id, activity_name = data[0], data[2]
    activity_dt, location, cost, photo = f"{data[3]} {str(data[4])[:5]}", data[5], data[9], data[12]
    contents = [
        info_text(f"地點: {location}"), 
        info_text(f"時間: {activity_dt}"),
        info_text(f"費用: {cost}")
    ]
    if not owner_info:
        attendee, people, condition = data[13], data[8], data[14]
        contents += [
            info_text(f"已報名人數: {attendee}/{people}"),
            info_text(f"狀態: {condition}"),
        ]
        footer = BoxComponent(
            layout = "horizontal",
            spacing = "sm",
            contents = [
                button("報名者資訊", f"報名者資訊_{activity_id}", "查看報名者資訊"),
                button("結束報名", f"結束報名_{activity_id}", "結束報名")
            ]
        )
    else:
        owner_name, owner_phone = owner_info 
        contents += [
            info_text(f"主揪: {owner_name}"),
            info_text(f"主揪電話: {owner_phone}")
        ]  
        footer = None 

    if "https://i.imgur.com/" not in photo:
        link = "https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip11.jpg"
    else:
        link = f"{photo}"
    
    activity_info = BubbleContainer(
        size = "kilo",
        direction = "ltr",
        header = BoxComponent(
            layout = "vertical",
            background_color = "#A7D5E1",
            contents = [
                TextComponent(
                    text = "活動詳細資訊",
                    size = "lg",
                    align = "start",
                    color = "#ffffff"
                )
            ]
        ),
        hero = ImageComponent(
            size = "full",
            aspectMode = "cover",
            aspectRatio = "320:213",
            url = f"{link}"
        ),
        body = BoxComponent(
            layout = "vertical",
            paddingAll = "13px",
            spacing = "md",
            contents = [
                info_text(activity_name, color = "#000000", size = "md", weight = "bold"),
                climate(activity_id, activity_name),
                BoxComponent(
                    layout = "vertical",
                    margin = "md",
                    spacing = "sm",
                    contents = contents
                )
            ]
        ),
        footer = footer
    )
    return activity_info

def registration_info(user_info, registration_id, activity_id):
    name, phone = user_info
    
    registration_info = BubbleContainer(
        size = "kilo",
        direction = "ltr",
        header = BoxComponent(
            layout = "vertical",
            background_color = "#A7D5E1",
            contents = [
                TextComponent(
                    text = "報名資訊",
                    size = "lg",
                    align = "start",
                    color = "#ffffff"
                )
            ]
        ),
        body = BoxComponent(
            layout = "vertical",
            paddingAll = "13px",
            spacing = "md",
            contents = [
                BoxComponent(
                    layout = "vertical",
                    margin = "md",
                    spacing = "sm",
                    contents = [
                        info_text(f"姓名: {name}", size = "md"),
                        info_text(f"電話: {phone}", size = "md")
                    ]
                )
            ]
        ),
        footer = BoxComponent(
            layout = "horizontal",
            spacing = "sm",
            contents = [
                button("取消報名", f"取消報名_{registration_id}_{activity_id}", "取消報名")
            ]
        )
    )
    return registration_info

def activity_registration_info(activity_data, owner_info, user_info, registration_id):
    activity_id = activity_data[0]
    info_content = [activity_info(activity_data, owner_info), registration_info(user_info, registration_id, activity_id)]

    activity_registration_info = FlexSendMessage(
        alt_text = "活動資訊與報名資訊",
        contents = CarouselContainer(
            contents = info_content
        )
    )
    return activity_registration_info

def send_activity_info(data):
    send_activity_info = FlexSendMessage(
        alt_text = "我的開團資訊",
        contents = activity_info(data)
    )

    return send_activity_info 
#--------------------------------------------------------------------------
def attendee_info(activity_name, attendee_data):
    print(attendee_data)
    if attendee_data:
        attendee_info = [f"{activity_name}", "報名者資訊："] + [f"{data[0]} {data[1]}" for data in attendee_data]
        attendee_info = TextSendMessage(
            text = "\n".join(attendee_info)
        )

    else:
        attendee_info = TextSendMessage(
            text = "目前無人報名"
        )

    return attendee_info
