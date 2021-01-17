from linebot.models import (
    TextSendMessage, MessageAction, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent, FillerComponent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,CarouselContainer
)
import datetime as dt
import json

list_type = TextSendMessage(
    text = "請選擇查詢 [歷史報名紀錄] 或 [我報名的團]",
    quick_reply = QuickReply(
        items = [
            QuickReplyButton(
                action = PostbackAction(label = "歷史報名紀錄", data = "rlist_已結束", display_text = "查詢[歷史報名紀錄]")
                ),
            QuickReplyButton(
                action = PostbackAction(label = "我報名的團", data = "rlist_進行中", display_text = "查詢[我報名的團]")
                )
            ]))

#我的報名列表
def rlist(data, type):
    if data:
        main = []
        for row in data:
            temp = BoxComponent(
                layout = "horizontal",
                contents = [
                    BoxComponent(
                        layout = "horizontal",
                        flex = 1,
                        contents = [
                            BoxComponent(
                                layout =  "baseline",
                                flex =  1,
                                contents = [
                                    IconComponent(
                                        url =  "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png",
                                        size =  "md"
                                    )
                                ]
                            )
                        ]
                    ),
                    BoxComponent(
                        layout = "horizontal",
                        flex =  9,
                        contents = [
                            TextComponent(
                                text =  f"{row[1]}",
                                align =  "start",
                                size = "md",
                                color = "#227C9D",
                                weight =  "regular",
                                margin= "sm",
                                action = PostbackAction(
                                    data = f"{row[0]}_查報名",
                                    display_text = f"{row[1]} 活動資訊與報名資訊"
                                )
                            )
                        ]
                    )
                ]
            )
            main.append(temp)
            if len(main)> 7:
                break

        bubble = BubbleContainer(
            size = "kilo",
            direction = "ltr",
            header = BoxComponent(
            layout = "horizontal",
            contents = [
                TextComponent(
                    text = f"我的報名列表({type})",
                    size = "lg",
                    weight = "bold",
                    color = "#AAAAAA"
                )
            ]
            ),
            body = BoxComponent(
                layout = "vertical",
                spacing = "md",
                contents = main
            ),
            footer = BoxComponent(
                layout = "horizontal",
                contents = [
                    ButtonComponent(
                        action = PostbackAction(
                            label =  "上一頁",
                            data =  "backward"
                        ),
                        height = "sm",
                        style = "primary",
                        color = "#A7D5E1",
                        gravity = "bottom"
                    ),
                    SeparatorComponent(
                        margin = "sm",
                        color = "#FFFFFF"
                    ),
                    ButtonComponent(
                        action = PostbackAction(
                        label = "下一頁",
                        data =  "forward"
                        ),
                        height = "sm",
                        style = "primary",
                        color = "#A7D5E1",
                        gravity = "bottom"
                    )
                ]
            )
        )

    else:
        bubble = BubbleContainer(
            direction = "ltr",
            body = BoxComponent(
                size = "xs",
                layout = "vertical",
                spacing =  "md",
                contents = [
                    TextComponent(
                        text =  f"目前無{type}的報名資料",
                        size =  "lg",
                        weight =  "bold",
                        color =  "#AAAAAA"
                    )
                ]
            )
        )

    msg = FlexSendMessage(
        alt_text = "報名列表",
        contents = bubble
    )

    return msg
    
 #活動資訊與報名資訊carousel
def carousel_registration(data_g, data_r):
    if "https://i.imgur.com/" not in data_g[12]:
        link = "https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip11.jpg"
    else:
        link = f"{data_g[12]}"
        
    group_info = BubbleContainer(
        size = "kilo",
        direction = "ltr",
        hero = ImageComponent(
            size = "full",
            aspectRatio = "16:9",
            aspectMode = "cover",
            url = f"{link}"
        ),
        body = BoxComponent(
            layout = "vertical",
            contents = [
                TextComponent(
                    text = f"活動詳細資訊",
                    weight = "bold",
                    size = "md",
                    wrap = True
                ),
                TextComponent(
                    text = f"{data_g[2]}", #activity_name
                    weight = "bold",
                    size = "md",
                    wrap = True
                ),
                BoxComponent(
                    layout = "vertical",
                    contents = [
                        BoxComponent(
                            layout = "vertical",
                            spacing = "sm",
                            contents = [
                                TextComponent(
                                    text = f"地點 {data_g[5]}",
                                    wrap = True,
                                    size = "sm",
                                    flex = 5
                                ),
                                TextComponent(
                                    text = f"時間 {data_g[3]} {str(data_g[4])[:5]}",
                                    size = "sm"
                                ),
                                TextComponent(
                                    text = f"費用 {data_g[9]}",
                                    size = "sm"
                                ),
                                TextComponent(
                                    text = f"主揪 {data_g[13]}",
                                    size = "sm"
                                ),
                                TextComponent(
                                    text = f"主揪電話 {data_g[14]}",
                                    size = "sm"
                                )
                            ]
                        )
                    ]
                )
            ],
        paddingAll = "13px",
        spacing = "md"
        )
    )

    bubbles = [group_info]

    for row in data_r:
        registrtion_info = BubbleContainer(
            size = "kilo",
            direction = "ltr",
            header = BoxComponent(
                layout = "vertical",
                contents = [
                    TextComponent(
                        text = "報名資訊",
                        weight = "bold",
                        size = "md",
                        align = "start",
                        color = "#000000"
                    )
                ]
            ),
            body = BoxComponent(
                layout = "vertical",
                contents = [
                    BoxComponent(
                        layout = "vertical",
                        contents = [
                            BoxComponent(
                                layout = "vertical",
                                spacing = "sm",
                                contents = [
                                    TextComponent(
                                        text = f"活動名稱：{row[2]}",
                                        size = "sm"
                                    ),
                                    TextComponent(
                                        text = f"姓名：{row[3]}",
                                        size = "sm"
                                    ),
                                    TextComponent(
                                        text = f"電話：{row[4]}",
                                        size = "sm"
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),
            footer = BoxComponent(
                layout = "horizontal",
                contents = [
                    ButtonComponent(
                        action = PostbackAction(
                            label = '取消報名',
                            display_text = "取消報名",
                            data = f"{row[0]}_{row[1]}_取消報名"
                            #row[0] registration_no    #row[1] activity_no
                        ),
                        height = "sm",
                        style = "primary",
                        color = "#A7D5E1",
                        gravity = "bottom"
                    )
                ]
            )
        )
        bubbles.append(registrtion_info)

    info_carousel = FlexSendMessage(
        alt_text = "活動資訊與報名資訊",
        contents = CarouselContainer(
            contents = bubbles
        )
    )
    return info_carousel
    
