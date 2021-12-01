from linebot.models import *
from templates import flexmsg_activity       

def quick_reply_button(activity_type):
    quick_reply_button = QuickReplyButton(
        action = PostbackAction(
            label = activity_type, 
            data = f"報名活動類型_{activity_type}",  
            display_text = activity_type
        )
    )
    return quick_reply_button

def activity_type():
    all_type = ["登山踏青", "桌遊麻將", "吃吃喝喝", "唱歌跳舞"]
    activity_type = TextSendMessage(
        text = "請選擇報名活動類型",
        quick_reply = QuickReply(
            items = [quick_reply_button(activity_type) for activity_type in all_type]
        )
    )
    return activity_type
#-----------------------------------------------------------------
def activity_in_index(activity_id, activity_name):
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
                    display_text = f"我想知道 {activity_name} 的詳細資訊",
                    data = f"詳細資訊_{activity_id}"
                )
            )
        ]
    )
    return activity_in_index

def page_button(new_page, activity_type, i):
    i = i - 8 if new_page == "上一頁" else i + 8
    page_button = ButtonComponent(
        action = PostbackAction(
            label = new_page,
            data = f"newPage_{activity_type}_{i}_",
            display_text = new_page
        ),
        height = "sm",
        style = "primary",
        color = "#A7D5E1",
        gravity = "bottom"
    )
    return page_button

def carousel_index(data, activity_type, i = 0):
    if i < 0:
        i = 0
    elif i >= len(data):
        i -= 8
    
    
    index_content = [activity_in_index(row[0], row[2]) for row in data[i: i+8]]
                    
    carousel_index = BubbleContainer(
        size = "kilo",
        direction = "ltr",
        header = BoxComponent(
            layout = "horizontal",
            contents = [
                TextComponent(
                    text = f"{activity_type}-活動列表",
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
                page_button("上一頁", activity_type, i),
                page_button("下一頁", activity_type, i)
            ]
        )
    )
    return carousel_index

def climate(activity_id, activity_name):
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
            data = f"climate_{activity_id}",
            display_text = f"{activity_name}的天氣預報"
        )
    )
    return climate

def carousel_text(text):
    carousel_text = TextComponent(
        text = text,
        wrap = True,
        color = "#8c8c8c",
        size = "xs",
    ) 
    return carousel_text   

def button(label, data, display_text):
    button = ButtonComponent(
        style = "link",
        height = "sm",
        color = "#229C8F",
        gravity = "bottom",
        action = PostbackAction(
            label = label,
            data = data,
            display_text = display_text
        )
    )
    return button   

def carousel(data, activity_type, i = 0):
    if i < 0:
        i = 0
    elif i >= len(data):
        i -= 8

    if data:
        carousel = [carousel_index(data, activity_type, i)] #第一頁的列表
        
        for row in data[i: i+8]:
            activity_id = row[0]
            activity_type = row[1]
            activity_name = row[2]
            activity_time = f"{row[3]} {str(row[4])[:5]}"
            location = row[5]
            cost = row[9]
            photo = row[12]
            
            if "https://i.imgur.com/" not in photo:
                link = "https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip11.jpg"
            else:
                link = f"{photo}"

            main = BubbleContainer(
                size = "kilo",
                direction = "ltr",
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
                        TextComponent(
                            text = f"{activity_name}",
                            weight = "bold",
                            size = "md",
                            wrap = True
                        ),
                        climate(activity_id, activity_name),
                        BoxComponent(
                            layout = "vertical",
                            margin = "md",
                            spacing = "sm",
                            contents = [
                                carousel_text(f"地點: {location}"),
                                carousel_text(f"時間: {activity_time}"),
                                carousel_text(f"費用: {cost}")
                            ]
                        )
                    ]
                ),
                footer = BoxComponent(
                    layout = "horizontal",
                    contents = [
                        button("立即報名", f"立即報名_{activity_id}", f"我要報名 {activity_name}！"),
                        SeparatorComponent(),
                        button("詳細資訊", f"詳細資訊_{activity_id}", f"我想知道 {activity_name} 的詳細資訊！")
                    ]
                )
            )
            carousel.append(main)

    else:
        carousel = [
            BubbleContainer(
                direction = "ltr",
                body = BoxComponent(
                    size = "xs",
                    layout = "vertical",
                    contents = [
                        TextComponent(
                            text = "目前無資料",
                            size = "lg",
                            weight = "bold",
                            color = "#AAAAAA"
                        )
                    ]
                )
            )
        ]

    msg_carousel = FlexSendMessage(
        alt_text = "可報名活動",
        contents = CarouselContainer(
            contents = carousel
        )
    )
    return msg_carousel
#-----------------------------------------------------------------
def more_info_header(activity_name):
    more_info_header = BoxComponent(
        layout = "vertical",
        contents = [
            TextComponent(
                text = f"{activity_name}\n 活動資訊如下：",
                weight = "bold",
                size = "lg",
                align = "start",
                color = "#000000"
            )
        ]
    )
    return more_info_header

def info_text(text, info):
    info_text = TextComponent(
        text = f"{text}：{info}",
        margin = "md",
        size = "md",
        wrap = True,
    )
    return info_text

def more_info_content(activity_info):
    activity_dt = f"{activity_info[2]}  {str(activity_info[3])[:5]}"

    more_info_content = []
    for i in [0, 1, 2, 4, 7, 8, 9, 10, 12]:    
        text, info = flexmsg_activity.columns_text[i], activity_info[i]
        if i == 3:
            info = activity_dt    
        more_info_content.append(info_text(text, info))  
    return more_info_content

def more_info(activity_info, activity_id):
    activity_name = activity_info[1]
    more_info = FlexSendMessage(
        alt_text = "詳細活動資訊",
        contents = BubbleContainer(
            direction = "ltr",
            header = more_info_header(activity_name),
            body = BoxComponent(
                layout = "vertical",
                contents = more_info_content(activity_info)
            ),
            footer = BoxComponent(
                layout = "vertical",
                contents = [
                    button("立即報名", f"立即報名_{activity_id}", f"我要報名 {activity_name}！")
                ]
            )
        )
    )
    return more_info
#---------------------------------------------------------------------
def duplication():
    duplication = FlexSendMessage(
        alt_text = "不可重複報名",
        contents = BubbleContainer(
            direction = "ltr",
            body = BoxComponent(
                size = "xs",
                layout = "vertical",
                contents = [
                    TextComponent(
                        text = "不可重複報名！ \n重新選擇想要報名的活動類型",
                        size = "lg",
                        weight = "bold",
                        color = "#AAAAAA",
                        wrap = True
                    )
                ]
            )
        )
    )

    duplication = [duplication, activity_type()]
    return duplication
#------------------------------------------------------------------------
def content(text, info):
    content = TextComponent(
        text = f"{text}：{info}",
        size = "md",
        flex = 5,
        align = "start",
        wrap = True,
    )
    return content

def edit(text, col):
    edit = TextComponent(
        text = "修改",
        size = "md",
        flex = 1,
        align = "end",
        gravity = "top",
        color = "#229C8F",
        action = PostbackAction(
            label = f"修改{text}",
            data = f"修改_users_{col}",
            display_text = f"修改{text}"
        )
    )
    return edit

def content_edit(info, text, col):
    content_edit = BoxComponent(
        layout = "horizontal",
        margin = "lg",
        contents = [
            content(text, info),
            SeparatorComponent(),
            edit(text, col)
        ]
    )
    return content_edit

def summary(data, activity_name):
    activity_id = data[2]
    registration_id = data[3]
    name = data[0]
    phone = data[1]

    summary = FlexSendMessage(
        alt_text = "請確認報名資訊",
        contents = BubbleContainer(
            direction = "ltr",
            header = BoxComponent(
                layout = "vertical",
                contents = [
                    TextComponent(
                        text = "請確認報名資訊：",
                        weight = "bold",
                        size = "lg",
                        align = "start",
                        color = "#000000"
                    )
                ]
            ),
            body = BoxComponent(
                layout = "vertical",
                contents = [
                    content("活動名稱", activity_name),
                    SeparatorComponent(
                        margin = "lg"
                    ),
                    content_edit(name, "姓名", "name"),
                    content_edit(phone, "電話", "phone")
                ]
            ),
            footer = BoxComponent(
                layout = "horizontal",
                contents = [
                    button("確認報名", f"確認報名_{activity_id}", "確認報名"),
                    SeparatorComponent(),
                    button("取消報名", f"取消報名_{registration_id}_{activity_id}", "取消報名")
                ]
            )
        )
    )
    return summary
