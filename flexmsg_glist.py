from linebot.models import *
import datetime as dt
import json

list_type = TextSendMessage(
    text = "�п�ܬd�� [�w����������] �� [�Y�N���{������]",
    quick_reply = QuickReply(
        items = [
            QuickReplyButton(
                action = PostbackAction(label = "���v�}�ά���", data = "�}�ά���_�w����", display_text = "�d��[�w����������]")
                ),
            QuickReplyButton(
                action = PostbackAction(label = "�Y�N���{������", data = "�}�ά���_�i�椤", display_text = "�d��[�Y�N���{������]")
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
                                     data = f"�}�θ�T_{row[0]}",  #activity_no
                                     display_text = f"�d�� {row[2]} ���ԲӸ�T"
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
                    text = f"�ڪ��}�ΦC�� ({type})",
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
                            label = "�W�@��",
                            data = f"backward_glist_{type}_{i-8}",
                            display_text = "�W�@��"
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
                            label = "�U�@��",
                            data = f"forward_glist_{type}_{i+8}",
                            display_text = "�U�@��"
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
                        text = f"�ثe�S��{type}�����W��ơI",
                        size = "lg",
                        weight = "bold",
                        color = "#AAAAAA"
                    )
                ]
            )
        )

    msg = FlexSendMessage(
        alt_text = "�ڪ��}��",
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
                    contents = [
                        BoxComponent(
                            layout = "vertical",
                            spacing = "sm",
                            contents = [
                                TextComponent(
                                    text = f"�a�I {data[5]}",
                                    wrap = True,
                                    size = "sm",
                                    flex = 5,
                                    ),
                                TextComponent(
                                    text = f"�ɶ� {data[3]} {str(data[4])[:5]}",
                                    size = "sm",
                                    ),
                                TextComponent(
                                    text = f"�O�� {data[9]}",
                                    size = "sm",
                                    ),
                                TextComponent(
                                    text = f"�w���W�H�� {data[15]}/{data[8]}",
                                    size = "sm",
                                    ),
                                TextComponent(
                                    text = f"���A {data[16]}",
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
                        label = "���W�̸�T",
                        data = f"���W�̸�T_{data[0]}",  #activity_no
                        display_text = "�d�ݳ��W�̸�T"
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
                        label = "�������W",
                        data = f"�������W_{data[0]}",  #activity_no
                        display_text = "�������W"
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
        alt_text = "�ڪ��}�θ�T",
        contents = bubble
            )
    return msg
    
