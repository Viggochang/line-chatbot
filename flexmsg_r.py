from linebot.models import *
import datetime as dt
import json

activity_type_for_attendee = TextSendMessage(
    text = "�п�ܳ��W��������",
    quick_reply = QuickReply(
        items = [
            QuickReplyButton(
                action = PostbackAction(label = "�n�s��C", data = "���W��������_�n�s��C",  display_text = "�n�s��C")
                ),
            QuickReplyButton(
                action = PostbackAction(label = "��C�±N", data = "���W��������_��C�±N", display_text = "��C�±N")
                ),
            QuickReplyButton(
                action = PostbackAction(label = "�Y�Y�ܳ�", data = "���W��������_�Y�Y�ܳ�", display_text = "�Y�Y�ܳ�")
                ),
            QuickReplyButton(
                action = PostbackAction(label = "�ۺq���R", data = "���W��������_�ۺq���R", display_text = "�ۺq���R")
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
                                        display_text = f"�ڷQ���D {row[2]} ���ԲӸ�T",
                                        data = f"{row[0]}_�ԲӸ�T"
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
                    text = f"{act_type}-���ΦC��",
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
                            label = "�W�@��",
                            data = f"backward_activity_{act_type}_{i-8}",
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
                            data = f"forward_activity_{act_type}_{i+8}",
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
        bubbles = [index]
        
        for row in data[i:]:
            
            if "https://i.imgur.com/" not in row[12]:
                link = "https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip11.jpg"
            else:
                link = f"{row[12]}"
                
            print("�ۤ��s��row[12] = ", row[12], "link = ",link)
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
                                            contents = [
                                                TextComponent(
                                                    text = f"�a�I: {row[5]}",
                                                    wrap = True,
                                                    color = "#8c8c8c",
                                                    size = "xs",
                                                    flex = 5,
                                                    ),
                                                TextComponent(
                                                    text = f"�ɶ�: {row[3]} {str(row[4])[:5]}",
                                                    color = "#8c8c8c",
                                                    size = "xs",
                                                    ),
                                                TextComponent(
                                                    text = f"�O��: {row[9]}",
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
                                        label = "�ߧY���W",
                                        data = f"�ߧY���W_{row[0]}_{row[2]}_{row[3]}",
                                        display_text = f"�ڭn���W {row[2]}�I"
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
                                        label = "�ԲӸ�T",
                                        data = f"{row[0]}_�ԲӸ�T",
                                        display_text = f"�ڷQ���D {row[2]} ���ԲӸ�T�I"
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
                        text = "�ثe�L���",
                        size = "lg",
                        weight = "bold",
                        color = "#AAAAAA"
                    )
                ]
            )
        )]

    msg_carousel = FlexSendMessage(
        alt_text = "�i���W����",
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
        alt_text = "�ԲӬ��ʸ�T",
        contents = BubbleContainer(
            direction = "ltr",
            header = BoxComponent(
                layout = "vertical",
                contents = [
                    TextComponent(
                        text = f"{data[2]}\n���ʸ�T�p�U�G",
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
                                  text = f"���ʦW�١G{data[2]}",
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
                                  text = f"���ʮɶ��G{data[3]} {str(data[4])[:5]}",
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
                                  text = f"���ʦa�I�G{data[5]}",
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
                                  text = f"���ʤH�ơG{data[8]}",
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
                                  text = f"���ʶO�ΡG{data[9]}",
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
                                  text = f"���W�I���G{data[10]}",
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
                                  text = f"���ʱԭz�G{data[11]}",
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
                                  text = f"�D���m�W�G{data[13]}",
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
                              label = "�ߧY���W",
                              data = f"�ߧY���W_{data[0]}_{data[2]}_{data[3]}",
                              display_text = f"�ڭn���W {data[2]}"
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
        alt_text = "�д��ѩm�W�μʺ�",
        contents = BubbleContainer(
            direction = "ltr",
            body = BoxComponent(
              layout = "vertical",
              contents = [
              TextComponent(
                  text = "�д��ѱz���m�W�άO�i�H���Ѥ��ʺ�",
                  size = "md",
                  wrap = True,
                  align = "center",
                  weight = "bold"
                  )
              ]
            ),
            #�i�ױ�������
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
            #�i�ױ�������/
        )
    )
    return name

def phone(progress):
    phone = FlexSendMessage(
        alt_text = "�д��ѹq��",
        contents = BubbleContainer(
            direction = "ltr",
            body = BoxComponent(
              layout = "vertical",
              contents = [
              TextComponent(
                  text = "�д��ѥi�H�p���z���q�ܸ��X",
                  size = "lg",
                  align = "center",
                  weight = "bold"
                  )
              ]
            ),
            #�i�ױ�������
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
            #�i�ױ�������/
        )
    )
    return phone

def summary_for_attend(data):
    summary = FlexSendMessage(
        alt_text = "�нT�{���W��T",
        contents = BubbleContainer(
            direction = "ltr",
            header = BoxComponent(
              layout = "vertical",
              contents = [
              TextComponent(
                  text = "�нT�{���W��T�G",
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
                                text = f"���ʧǸ��G{data[1]}",
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
                                text = f"���ʦW�١G{data[2]}",
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
                                text = f"�m�W�G{data[3]}",
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
                                text = "�ק�",
                                size = "md",
                                align = "end",
                                gravity = "top",
                                weight = "bold",
                                action = PostbackAction(
                                    label = "�ק�m�W",
                                    data = "�ק���W_attendee_name",
                                    display_text = "�ק�m�W"
                                )
                            )
                        ]
                    ),
                    BoxComponent(
                        layout = "horizontal",
                        contents = [
                            TextComponent(
                                text = f"�q�ܡG{data[4]}",
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
                                text = "�ק�",
                                size = "md",
                                align = "end",
                                gravity = "top",
                                weight = "bold",
                                action = PostbackAction(
                                    label = "�ק�q��",
                                    data = "�ק���W_phone",
                                    display_text = "�ק�q��"
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
                            label = "�T�{���W",
                            data = "�T�{���W",
                            display_text = "�T�{���W"
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
                            label = "�������W",
                            data = "~cancel",
                            display_text = "�������W"
                        )
                    )
                ]
            )
        )
    )
    return summary
