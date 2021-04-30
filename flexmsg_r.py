# -*- coding: utf-8 -*-

from linebot.models import *
import datetime as dt
import json

activity_type_for_attendee = TextSendMessage(
    text = "請選擇報名活動類型",
    quick_reply = QuickReply(
        items = [
            QuickReplyButton(
                action = PostbackAction(label = "登山踏青", data = "報名活動類型_登山踏青",  display_text = "登山踏青")
                ),
            QuickReplyButton(
                action = PostbackAction(label = "桌遊麻將", data = "報名活動類型_桌遊麻將", display_text = "桌遊麻將")
                ),
            QuickReplyButton(
                action = PostbackAction(label = "吃吃喝喝", data = "報名活動類型_吃吃喝喝", display_text = "吃吃喝喝")
                ),
            QuickReplyButton(
                action = PostbackAction(label = "唱歌跳舞", data = "報名活動類型_唱歌跳舞", display_text = "唱歌跳舞")
                )
            ]))


def carousel(data, act_type, i = 0):

    if data:
        if i < 0:
            i = 0
        elif i >= len(data):
            i -= 8
        
        act_lst = []
                    
        for row in data[i:]:
            temp = BoxComponent(
                layout = "horizontal",
                contents = [
                    BoxComponent(
                        layout = "horizontal",
                        flex =  1,
                        contents = [
                            BoxComponent(
                                layout = "baseline",
                                flex =  1,
                                contents = [
                                    IconComponent(
                                        url =  "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png",
                                        size =  "sm"
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
                                text = f"{row[2]}",
                                align = "start",
                                size = "md",
                                color = "#227C9D",
                                weight = "regular",
                                margin= "sm",
                                action = PostbackAction(
                                        display_text = f"我想知道 {row[2]} 的詳細資訊",
                                        data = f"{row[0]}_詳細資訊"
                                        )
                            )
                        ]
                    )
                ]
            )
            act_lst.append(temp)
            if len(act_lst) >= 8:
                break
                
        index = BubbleContainer(
            size = "kilo",
            direction = "ltr",
            header = BoxComponent(
                layout = "horizontal",
                contents = [
                    TextComponent(
                        text = f"{act_type}-揪團列表",
                        size = "lg",
                        weight = "bold",
                        color = "#AAAAAA"
                    )
                ]
            ),
            body = BoxComponent(
                layout = "vertical",
                spacing = "md",
                contents = act_lst
            ),
            footer = BoxComponent(
                layout = "horizontal",
                contents = [
                    ButtonComponent(
                        action = PostbackAction(
                            label = "上一頁",
                            data = f"backward_activity_{act_type}_{i-8}",
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
                            data = f"forward_activity_{act_type}_{i+8}",
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
        bubbles = [index] #第一頁的列表
        
        for row in data[i:]:
            
            if "https://i.imgur.com/" not in row[12]:
                link = "https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip11.jpg"
            else:
                link = f"{row[12]}"
                
            print("相片連結row[12] = ", row[12], "link = ",link)
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
                            contents = [
                                TextComponent(
                                    text = f"{row[2]}",
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
                                                        data = f"climate_{row[0]}",
                                                        display_text = f"{row[2]}的天氣預報"
                                                    )
                                                )
                                            ]
                                        ),
                                        BoxComponent(
                                            layout = "vertical",
                                            spacing = "sm",
                                            margin = "sm",
                                            contents = [
                                                TextComponent(
                                                    text = f"地點: {row[5]}",
                                                    wrap = True,
                                                    color = "#8c8c8c",
                                                    size = "xs",
                                                    flex = 5,
                                                    ),
                                                TextComponent(
                                                    text = f"時間: {row[3]} {str(row[4])[:5]}",
                                                    color = "#8c8c8c",
                                                    size = "xs",
                                                    ),
                                                TextComponent(
                                                    text = f"費用: {row[9]}",
                                                    color = "#8c8c8c",
                                                    size = "xs",
                                                    ),
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
                                    style = "link",
                                    action = PostbackAction(
                                        label = "立即報名",
                                        data = f"立即報名_{row[0]}_{row[1]}_{row[2]}_{row[3]}",
                                        display_text = f"我要報名 {row[2]}！"
                                    ),
                                    height = "sm",
                                    margin = "none",
                                    color = "#229C8F",
                                    gravity = "bottom"
                                    ),
                                SeparatorComponent(),
                                ButtonComponent(
                                    style = "link",
                                    action = PostbackAction(
                                        label = "詳細資訊",
                                        data = f"{row[0]}_詳細資訊",
                                        display_text = f"我想知道 {row[2]} 的詳細資訊！"
                                        ),
                                    height = "sm",
                                    margin = "none",
                                    color = "#229C8F",
                                    gravity = "bottom"
                                    )
                                ]
                            )
                        )
            bubbles.append(main)
            if len(bubbles) >= 9:
                break
    else:
        bubbles = [BubbleContainer(
            direction = "ltr",
            body = BoxComponent(
                size = "xs",
                layout = "vertical",
                spacing = "md",
                contents = [
                    TextComponent(
                        text = "目前無資料",
                        size = "lg",
                        weight = "bold",
                        color = "#AAAAAA"
                    )
                ]
            )
        )]

    msg_carousel = FlexSendMessage(
        alt_text = "可報名活動",
        contents = CarouselContainer(
            contents = bubbles
            )
        )
    return msg_carousel

def MoreInfoSummary(data):
    if "https://i.imgur.com/" not in data[12]:
        act = None
        col = "#141414"
    else:
        act=URIAction(uri = f"{data[12]}")
        col = "#229C8F"
    summary = FlexSendMessage(
        alt_text = "詳細活動資訊",
        contents = BubbleContainer(
            direction = "ltr",
            header = BoxComponent(
                layout = "vertical",
                contents = [
                    TextComponent(
                        text = f"{data[2]}\n活動資訊如下：",
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
                      BoxComponent(
                          layout = "horizontal",
                          contents = [
                              TextComponent(
                                  text = f"活動名稱：{data[2]}",
                                  size = "md",
                                  flex = 10,
                                  align = "start"
                              )
                          ]
                      ),
                      BoxComponent(
                          layout = "horizontal",
                          contents = [
                              TextComponent(
                                  text = f"活動時間：{data[3]} {str(data[4])[:5]}",
                                  size = "md",
                                  flex = 10,
                                  align = "start"
                              )
                          ]
                      ),
                      BoxComponent(
                          layout = "horizontal",
                          contents = [
                              TextComponent(
                                  text = f"活動地點：{data[5]}",
                                  size = "md",
                                  flex = 10,
                                  wrap = True,
                                  align = "start"
                              )
                          ]
                      ),
                      BoxComponent(
                          layout = "horizontal",
                          contents = [
                              TextComponent(
                                  text = f"活動人數：{data[8]}",
                                  size = "md",
                                  flex = 10,
                                  align = "start"
                              )
                          ]
                      ),
                      BoxComponent(
                          layout = "horizontal",
                          contents = [
                              TextComponent(
                                  text = f"活動費用：{data[9]}",
                                  size = "md",
                                  flex = 10,
                                  align = "start"
                              )
                          ]
                      ),
                      BoxComponent(
                          layout = "horizontal",
                          contents = [
                              TextComponent(
                                  text = f"報名截止日：{data[10]}",
                                  size = "md",
                                  flex = 10,
                                  align = "start"
                              )
                          ]
                      ),
                      BoxComponent(
                          layout = "horizontal",
                          contents = [
                              TextComponent(
                                  text = f"活動敘述：{data[11]}",
                                  size = "md",
                                  flex = 10,
                                  align = "start"
                              )
                          ]
                      ),
                      BoxComponent(
                          layout = "horizontal",
                          contents = [
                              TextComponent(
                                  text = f"主揪姓名：{data[13]}",
                                  size = "md",
                                  flex = 10,
                                  align = "start"
                              )
                          ]
                      )
                  ]
              ),
              footer = BoxComponent(
                  layout = "vertical",
                  contents = [
                      ButtonComponent(
                          style = "link",
                          height = "sm",
                          margin = "none",
                          color = "#229C8F",
                          gravity = "bottom",
                          action = PostbackAction(
                              label = "立即報名",
                              data = f"立即報名_{data[0]}_{data[1]}_{data[2]}_{data[3]}",
                              display_text = f"我要報名 {data[2]}"
                          )
                      )
                  ]
              )
        )
    )
    return summary


def flex(i, progress):
    if i == 3 or i == "attendee_name":
        msg = name(progress)
    elif i == 4 or i == "phone":
        msg = phone(progress)
        
    return msg

def name(progress):
    name = FlexSendMessage(
        alt_text = "請提供姓名或暱稱",
        contents = BubbleContainer(
            direction = "ltr",
            body = BoxComponent(
              layout = "vertical",
              contents = [
              TextComponent(
                  text = "請提供您的姓名或是可以辨識之暱稱",
                  size = "md",
                  wrap = True,
                  align = "center",
                  weight = "bold"
                  )
              ]
            ),
            #進度條的本體
            footer=BoxComponent(
                layout = "vertical",
                margin = "md",
                contents = [TextComponent(text = f"{progress[6]} / {progress[0]} ", weight = "bold", size = "md"),
                            BoxComponent(layout = "vertical",
                                         margin = "md",
                                         contents = [
                                             BoxComponent(layout = "vertical",
                                                          contents = [FillerComponent()]
                                                         )
                                         ],
                                         width = f"{int(progress[6] / progress[0] * 100 + 0.5 )}%",
                                         background_color = "#3DE1D0",
                                         height = "6px"
                                        )
                           ]
            )
            #進度條的本體/
        )
    )
    return name

def phone(progress):
    phone = FlexSendMessage(
        alt_text = "請提供電話",
        contents = BubbleContainer(
            direction = "ltr",
            body = BoxComponent(
              layout = "vertical",
              contents = [
              TextComponent(
                  text = "請提供可以聯絡您的電話號碼",
                  size = "lg",
                  align = "center",
                  weight = "bold"
                  )
              ]
            ),
            #進度條的本體
            footer = BoxComponent(
                layout = "vertical",
                margin = "md",
                contents = [TextComponent(text = f"{progress[7]} / {progress[0]} ", weight = "bold", size = "md"),
                            BoxComponent(layout = "vertical",
                                         margin = "md",
                                         contents = [
                                             BoxComponent(layout = "vertical",
                                                          contents = [FillerComponent()]
                                                         )
                                         ],
                                         width = f"{int(progress[7] / progress[0] * 100 + 0.5 )}%",
                                         background_color = "#3DE1D0",
                                         height = "6px"
                                        )
                           ]
            )
            #進度條的本體/
        )
    )
    return phone

def summary_for_attend(data):
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
                    BoxComponent(
                        layout = "horizontal",
                        contents = [
                            TextComponent(
                                text = f"活動序號：{data[1]}",
                                size = "md",
                                flex = 10,
                                align = "start"
                            ),
                            SeparatorComponent(
                                margin = "lg"
                            )
                        ]
                    ),
                    BoxComponent(
                        layout = "horizontal",
                        contents = [
                            TextComponent(
                                text = f"活動名稱：{data[2]}",
                                size = "md",
                                flex = 10,
                                align = "start"
                            ),
                            SeparatorComponent(
                                margin = "lg"
                            )
                        ]
                    ),
                    BoxComponent(
                        layout = "horizontal",
                        contents = [
                            TextComponent(
                                text = f"姓名：{data[3]}",
                                size = "md",
                                flex = 10,
                                align = "start"
                            ),
                            SeparatorComponent(
                                margin = "lg"
                            )
                        ]
                    ),
                    BoxComponent(
                        layout = "horizontal",
                        contents = [
                            TextComponent(
                                text = "修改",
                                size = "md",
                                align = "end",
                                gravity = "top",
                                weight = "bold",
                                action = PostbackAction(
                                    label = "修改姓名",
                                    data = "修改報名_attendee_name",
                                    display_text = "修改姓名"
                                )
                            )
                        ]
                    ),
                    BoxComponent(
                        layout = "horizontal",
                        contents = [
                            TextComponent(
                                text = f"電話：{data[4]}",
                                size = "md",
                                flex = 10,
                                align = "start"
                            ),
                            SeparatorComponent(
                                margin = "lg"
                            )
                        ]
                    ),
                    BoxComponent(
                        layout = "horizontal",
                        contents = [
                            TextComponent(
                                text = "修改",
                                size = "md",
                                align = "end",
                                gravity = "top",
                                weight = "bold",
                                action = PostbackAction(
                                    label = "修改電話",
                                    data = "修改報名_phone",
                                    display_text = "修改電話"
                                )
                            )
                        ]
                    )
                ]
            ),
            footer = BoxComponent(
                layout = "horizontal",
                contents = [
                    ButtonComponent(
                        style = "link",
                        height = "sm",
                        margin = "none",
                        color = "#229C8F",
                        gravity = "bottom",
                        action = PostbackAction(
                            label = "確認報名",
                            data = "確認報名",
                            display_text = "確認報名"
                        )
                    ),
                    SeparatorComponent(),
                    ButtonComponent(
                        style = "link",
                        height = "sm",
                        margin = "none",
                        color = "#229C8F",
                        gravity = "bottom",
                        action = PostbackAction(
                            label = "取消報名",
                            data = "~cancel",
                            display_text = "取消報名"
                        )
                    )
                ]
            )
        )
    )
    return summary
