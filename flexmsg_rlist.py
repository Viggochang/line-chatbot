from linebot.models import *
import datetime as dt
import json

list_type = TextSendMessage(
    text = "�п�ܬd�� [���v���W����] �� [�ڳ��W����]",
    quick_reply = QuickReply(
        items = [
            QuickReplyButton(
                action = PostbackAction(label = "���v���W����", data = "���W����_�w����", display_text = "�d��[���v���W����]")
                ),
            QuickReplyButton(
                action = PostbackAction(label = "�ڳ��W����", data = "���W����_�i�椤", display_text = "�d��[�ڳ��W����]")
                )
            ]))

#�ڪ����W�C��
def rlist(data, type, i = 0):
    if data:
        if i < 0:
            i = 0
        elif i >= len(data):
            i -= 8
            
        registration_lst = []
        for row in data[i:]:
            temp = BoxComponent(
                layout = "horizontal",
                contents = [
                    BoxComponent(
                        layout = "horizontal",
                        flex = 1,
                        contents = [
                            BoxComponent(
                                layout = "baseline",
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
                                text = f"{row[1]}",
                                align = "start",
                                size = "md",
                                color = "#227C9D",
                                weight = "regular",
                                margin= "sm",
                                action = PostbackAction(
                                    data = f"{row[0]}_�d���W",
                                    display_text = f"{row[1]} ���ʸ�T�P���W��T"
                                )
                            )
                        ]
                    )
                ]
            )
            
            registration_lst.append(temp)
            if len(registration_lst) >= 7:
                break

        bubble = BubbleContainer(
            size = "kilo",
            direction = "ltr",
            header = BoxComponent(
            layout = "horizontal",
            contents = [
                TextComponent(
                    text = f"�ڪ����W�C��({type})",
                    size = "lg",
                    weight = "bold",
                    color = "#AAAAAA"
                )
            ]
            ),
            body = BoxComponent(
                layout = "vertical",
                spacing = "md",
                contents = registration_lst
            ),
            footer = BoxComponent(
                layout = "horizontal",
                contents = [
                    ButtonComponent(
                        action = PostbackAction(
                            label =  "�W�@��",
                            data = f"backward_rlist_{type}_{i-8}",
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
                            data = f"forward_rlist_{type}_{i+8}",
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
                        text = f"�ثe�S��{type}�����W���",
                        size = "lg",
                        weight = "bold",
                        color = "#AAAAAA"
                    )
                ]
            )
        )

    msg = FlexSendMessage(
        alt_text = "���W�C��",
        contents = bubble
    )

    return msg
    
 #���ʸ�T�P���W��Tcarousel
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
                    text = f"���ʸԲӸ�T",
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
                                    text = f"�a�I {data_g[5]}",
                                    wrap = True,
                                    size = "sm",
                                    flex = 5
                                ),
                                TextComponent(
                                    text = f"�ɶ� {data_g[3]} {str(data_g[4])[:5]}",
                                    size = "sm"
                                ),
                                TextComponent(
                                    text = f"�O�� {data_g[9]}",
                                    size = "sm"
                                ),
                                TextComponent(
                                    text = f"�D�� {data_g[13]}",
                                    size = "sm"
                                ),
                                TextComponent(
                                    text = f"�D���q�� {data_g[14]}",
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
                        text = "���W��T",
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
                                        text = f"���ʦW�١G{row[2]}",
                                        size = "sm"
                                    ),
                                    TextComponent(
                                        text = f"�m�W�G{row[3]}",
                                        size = "sm"
                                    ),
                                    TextComponent(
                                        text = f"�q�ܡG{row[4]}",
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
                            label = '�������W',
                            display_text = "�������W",
                            data = f"{row[0]}_{row[1]}_�������W"
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
        alt_text = "���ʸ�T�P���W��T",
        contents = CarouselContainer(
            contents = bubbles
        )
    )
    return info_carousel
    
