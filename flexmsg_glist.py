# -*- coding: utf-8 -*-

from linebot.models import *
import datetime as dt
import json

list_type = TextSendMessage(
    text = "請選擇查詢 [已結束的活動] 或 [即將來臨的活動]",
    quick_reply = QuickReply(
        items = [
            QuickReplyButton(
                action = PostbackAction(label = "歷史開團紀錄", data = "開團紀錄_已結束", display_text = "查詢[已結束的活動]")
                ),
            QuickReplyButton(
                action = PostbackAction(label = "即將來臨的活動", data = "開團紀錄_進行中", display_text = "查詢[即將來臨的活動]")
                )
            ]))


def glist(data, type, i = 0):
    if data:
        if i < 0:
            i = 0
        elif i >= len(data):
            i -= 8
            
        group_lst = []
        #row [activity_no, activity_type, activity_name, activity_date, activity_time, activity_title, ...]
        for row in data[i:]:
            activity = BoxComponent(
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
                                 text = f"{row[2]}", #activity_name
                                 align = "start",
                                 size = "md",
                                 color = "#227C9D",
                                 weight = "regular",
                                 margin= "sm",
                                 action = PostbackAction(
                                     data = f"開團資訊_{row[0]}",  #activity_no
                                     display_text = f"查看 {row[2]} 的詳細資訊"
                                     )
                             )
                         ]
                     )
                 ]
             )

            group_lst.append(activity)
            if len(group_lst) >= 8:
                break
            
        bubble = BubbleContainer(
            size = "kilo",
            direction = "ltr",
            header = BoxComponent(
            layout = "horizontal",
            contents = [
                TextComponent(
                    text = f"我的開團列表 ({type})",
                    size = "lg",
                    weight = "bold",
                    color = "#AAAAAA"
                )
            ]
            ),
            body = BoxComponent(
                layout = "vertical",
                spacing = "md",
                contents = group_lst
            ),
            footer = BoxComponent(
                layout = "horizontal",
                contents = [
                    ButtonComponent(
                        action = PostbackAction(
                            label = "上一頁",
                            data = f"backward_glist_{type}_{i-8}",
                            display_text = "上一頁"
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
                            data = f"forward_glist_{type}_{i+8}",
                            display_text = "下一頁"
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
                spacing = "md",
                contents = [
                    TextComponent(
                        text = f"目前沒有開團資料！",
                        size = "lg",
                        weight = "bold",
                        color = "#AAAAAA"
                    )
                ]
            )
        )

    msg = FlexSendMessage(
        alt_text = "我的開團",
        contents = bubble
        )
        
    return msg
    

def MyGroupInfo(data):
    if "https://i.imgur.com/" not in data[12]:
        link="https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip11.jpg"
    else:
        link = f"{data[12]}"
        
    bubble = BubbleContainer(
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
            contents = [
                TextComponent(
                    text = f"{data[2]}",
                    weight = "bold",
                    size = "md",
                    wrap = True
                ),
                BoxComponent(
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
                            offset_top = "2.5px",
                            action = PostbackAction(
                                label = "天氣預報",
                                data = f"climate_{data[0]}",
                                display_text = f"{data[2]}的天氣預報"
                            )
                        )
                    ]
                ),
                BoxComponent(
                    layout = "vertical",
                    contents = [
                        BoxComponent(
                            layout = "vertical",
                            spacing = "sm",
                            contents = [
                                TextComponent(
                                    text = f"地點: {data[5]}",
                                    wrap = True,
                                    color = "#8c8c8c",
                                    size = "sm",
                                    flex = 5,
                                    ),
                                TextComponent(
                                    text = f"時間: {data[3]} {str(data[4])[:5]}",
                                    color = "#8c8c8c",
                                    size = "sm",
                                    ),
                                TextComponent(
                                    text = f"費用: {data[9]}",
                                    color = "#8c8c8c",
                                    size = "sm",
                                    ),
                                TextComponent(
                                    text = f"已報名人數: {data[15]}/{data[8]}",
                                    color = "#8c8c8c",
                                    size = "sm",
                                    ),
                                TextComponent(
                                    text = f"狀態: {data[16]}",
                                    color = "#8c8c8c",
                                    size = "sm",
                                    )
                                ]
                            )
                        ]
                    )
                ],
            paddingAll = "13px",
            spacing = "md",
            ),
        footer = BoxComponent(
            layout = "horizontal",
            contents = [
                ButtonComponent(
                    style = "primary",
                    action = PostbackAction(
                        label = "報名者資訊",
                        data = f"報名者資訊_{data[0]}",  #activity_no
                        display_text = "查看報名者資訊"
                        ),
                    height = "sm",
                    margin = "none",
                    gravity = "bottom",
                    color = "#A7D5E1"
                    ),
                SeparatorComponent(
                    margin = "sm",
                    color = "#FFFFFF"
                    ),
                ButtonComponent(
                    style = "primary",
                    action = PostbackAction(
                        label = "結束報名",
                        data = f"結束報名_{data[0]}",  #activity_no
                        display_text = "結束報名"
                        ),
                    height = "sm",
                    margin = "none",
                    gravity = "bottom",
                    color = "#A7D5E1"
                    )
                ]
                )
            )
    
    msg = FlexSendMessage(
        alt_text = "我的開團資訊",
        contents = bubble
            )
    return msg
    
