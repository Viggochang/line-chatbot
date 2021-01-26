from linebot.models import *
import datetime as dt
import json

activity_type = TextSendMessage(
    text = "�п�ܶ}�ά�������",
    quick_reply = QuickReply(
        items = [
            QuickReplyButton(
                action = PostbackAction(label = "�n�s��C", data = "�}�ά�������_�n�s��C",  display_text = "�n�s��C")
                ),
            QuickReplyButton(
                action = PostbackAction(label = "��C�±N", data = "�}�ά�������_��C�±N", display_text = "��C�±N")
                ),
            QuickReplyButton(
                action = PostbackAction(label = "�Y�Y�ܳ�", data = "�}�ά�������_�Y�Y�ܳ�", display_text = "�Y�Y�ܳ�")
                ),
            QuickReplyButton(
                action = PostbackAction(label = "�ۺq���R", data = "�}�ά�������_�ۺq���R", display_text = "�ۺq���R")
                )
            ]))
            
# ���}�Ϊ̥Ϊ�
def flex(i, data, progress):
    if i == 2 or i == "activity_name":
        msg = activity_name(progress)
    elif i == 3 or i == "activity_date":
        msg = activity_time(progress)
    elif i == 5 or i == "location_tittle":
        msg = location(progress)
    elif i == 8 or i == "people":
        msg = people(progress)
    elif i == 9 or i == "cost":
        msg = cost(progress)
    elif i == 10 or i == "due_date":
        msg = due_time(data)
    elif i == 11 or i == "description":
        msg = description
    elif i == 12 or i == "photo":
        msg = photo
    elif i == 13 or i == "name":
        msg = name(progress)
    elif i == 14 or i == "phone":
        msg = phone(progress)
    elif i == 1 or i == "activity_type":
        msg = activity_type
    else:
        msg = TextSendMessage(text = "FlexMessage Bug �z�o��...")
    return msg

def activity_name(progress):
    activity_name = FlexSendMessage(
        alt_text = "�ж�g���ʦW��",
        contents = BubbleContainer(
            direction = "ltr",
            body = BoxComponent(
                layout = "vertical",
                contents = [
                    TextComponent(text = "���ʦW��", weight = "bold", size = "lg", align = "center"),
                    BoxComponent(layout = "baseline",
                                 margin = "lg",
                                 contents = [
                                     TextComponent(text = "�аݱz�����ʦW�٭n�s����O�H",
                                                   size = "md",
                                                   flex = 0,
                                                   color = "#666666")
                                 ]
                                )
                ]
            ),
            #�i�ױ�������
            footer=BoxComponent(
                layout = "vertical",
                margin = "md",
                contents = [TextComponent(text = f"{progress[1]} / {progress[0]} ", weight = "bold", size = "md"),
                            BoxComponent(layout = "vertical",
                                         margin = "md",
                                         contents = [
                                             BoxComponent(layout = "vertical",
                                                          contents = [FillerComponent()]
                                                         )
                                         ],
                                         width = f"{int(progress[1] / progress[0] * 100 + 0.5 )}%",
                                         background_color = "#3DE1D0",
                                         height = "6px"
                                        )
                           ]
            )
            #�i�ױ�������/
        )
    )
    return activity_name

def activity_time(progress):
    activity_time = FlexSendMessage(
        alt_text = "�ЬD�ﬡ�ʮɶ�",
        contents = BubbleContainer(
            direction = "ltr",
            body = BoxComponent(
                layout = "vertical",
                contents =[
                    TextComponent(
                        text = "�п�ܬ��ʮɶ�",
                        size = "lg",
                        align = "center",
                        weight = "bold"
                    )
                ]
            ),
            footer = BoxComponent(
              layout = "vertical",
              contents = [
                  BoxComponent(layout = "vertical",
                                 margin = "md",
                                 contents = [TextComponent(text = f"{progress[2]} / {progress[0]} ", weight = "bold", size = "md"),
                                             BoxComponent(layout = "vertical",
                                                          margin = "md",
                                                          contents = [
                                                              BoxComponent(layout = "vertical",
                                                                           contents = [FillerComponent()]
                                                                          )
                                                          ],
                                                          width = f"{int(progress[2] / progress[0] * 100 + 0.5 )}%",
                                                          background_color = "#3DE1D0",
                                                          height = "6px"
                                                         )

                                            ]
                              ),
                  BoxComponent(layout = "vertical",
                                 margin = "md",
                                 contents = [
                                     ButtonComponent(
                                         DatetimePickerAction(
                                             label = "�I�ڿ�ɶ�",
                                             data = "activity_time",
                                             mode = "datetime"
                                         ),
                                         height = "sm",
                                         margin = "none",
                                         style = "primary",
                                         color = "#A7D5E1",
                                         gravity = "bottom"
                                     )
                                 ]
                              )
              ]
            )
        )
    )
    return activity_time

def location(progress):
    location = FlexSendMessage(
        alt_text = "�ЬD�ﬡ�ʦa�I",
        contents = BubbleContainer(
            direction = "ltr",
            body = BoxComponent(
              layout = "vertical",
              contents = [
              TextComponent(
                  text = "�п�ܬ��ʦa�I",
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
                contents = [BoxComponent(layout = "vertical",
                                 margin = "md",
                                 contents = [TextComponent(text = f"{progress[3]} / {progress[0]} ",
                                                           weight = "bold",
                                                           size = "md"),
                                             BoxComponent(layout = "vertical",
                                                          margin = "md",
                                                          contents = [
                                                              BoxComponent(layout = "vertical",
                                                                           contents = [FillerComponent()]
                                                                          )
                                                          ],
                                                          width = f"{int(progress[3] / progress[0] * 100 + 0.5 )}%",
                                                          background_color = "#3DE1D0",
                                                          height = "6px"
                                                         )

                                            ]
                              ),
            #�i�ױ�������/
            BoxComponent(
              layout = "horizontal",
                margin = "md",
              contents = [
                ButtonComponent(
                    URIAction(
                        label = "�I�ڿ�a�I",
                        uri = "https://line.me/R/nv/location"
                    ),
                    height = "sm",
                    margin = "none",
                    style = "primary",
                    color = "#A7D5E1",
                    gravity = "bottom"
                )
              ]
            )
                           ]
            )
        )
    )
    return location

def people(progress):
    people = FlexSendMessage(
        alt_text = "�ж�g�H��",
        contents = BubbleContainer(
            direction = "ltr",
            body = BoxComponent(
              layout = "vertical",
              contents =[
              TextComponent(
                  text = "�ж�g���ʰѥ[�H��",
                  size = "lg",
                  align = "center",
                  weight = "bold"
                  )
              ]
            ),
            #�i�ױ�������
            footer=BoxComponent(
                layout = "vertical",
                margin = "md",
                contents = [TextComponent(text = f"{progress[4]} / {progress[0]} ", weight = "bold", size = "md"),
                            BoxComponent(layout = "vertical",
                                         margin = "md",
                                         contents = [
                                             BoxComponent(layout = "vertical",
                                                          contents = [FillerComponent()]
                                                         )
                                         ],
                                         width = f"{int(progress[4] / progress[0] * 100 + 0.5 )}%",
                                         background_color = "#3DE1D0",
                                         height = "6px"
                                        )
                           ]
            )
            #�i�ױ�������/
        )
    )
    return people
    
def cost(progress):
    cost = FlexSendMessage(
        alt_text = "�ж�g�w�p��X",
        contents = BubbleContainer(
            direction = "ltr",
            body = BoxComponent(
              layout = "vertical",
              contents = [
              TextComponent(
                  text = "�ж�g�w�p��X",
                  size = "lg",
                  align = "center",
                  weight = "bold"
                  )
              ]
            ),
            #�i�ױ�������
            footer=BoxComponent(
                layout = "vertical",
                margin = "md",
                contents = [TextComponent(text = f"{progress[5]} / {progress[0]} ", weight = "bold", size = "md"),
                            BoxComponent(layout = "vertical",
                                         margin = "md",
                                         contents = [
                                             BoxComponent(layout = "vertical",
                                                          contents = [FillerComponent()]
                                                         )
                                         ],
                                         width = f"{int(progress[5] / progress[0] * 100 + 0.5 )}%",
                                         background_color = "#3DE1D0",
                                         height = "6px"
                                        )
                           ]
            )
            #�i�ױ�������/
        )
    )
    return cost

def due_time(data):
    due = FlexSendMessage(
        alt_text = "�ЬD��I����",
        contents = BubbleContainer(
            direction = "ltr",
            body = BoxComponent(
              layout = "vertical",
              contents = [
              TextComponent(
                  text = "�п�ܳ��W�I����",
                  size = "lg",
                  align = "center",
                  weight = "bold"
                  )
              ]
            ),
            #�i�ױ�������
        footer=
        #�i�ױ�������/
            BoxComponent(
                layout = "horizontal",
                contents = [ButtonComponent(
                    DatetimePickerAction(
                        label = "�I�ڿ�ɶ�",
                        data = "due_time",
                        mode = "date",
                        max = str(data[3])
                    ),
                    height = "sm",
                    margin = "none",
                    style = "primary",
                    color = "#A7D5E1",
                    gravity = "bottom"
                )
              ]
            )
        )
    )
    return due

description = FlexSendMessage(
    alt_text = "�ж�g���ʤ��e",
    contents = BubbleContainer(
        direction = "ltr",
        body = BoxComponent(
          layout = "vertical",
          contents = [
          TextComponent(
              text = "�ж�g�ԲӬ��ʤ��e",
              size = "lg",
              align = "center",
              weight = "bold"
              )
          ]
        )
    )
)

photo = FlexSendMessage(
    alt_text = "�жǰe�@�i�Ӥ�",
    contents = BubbleContainer(
        direction = "ltr",
        body = BoxComponent(
          layout = "vertical",
          contents = [
          TextComponent(
              text = "�жǰe�@�i�Ӥ�",
              size = "md",
              wrap = True,
              align = "center",
              weight = "bold"
              )
          ]
        )
    )
)
def name(progress):
    name = FlexSendMessage(
        alt_text = "�д��ѦW��",
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

#mail = FlexSendMessage(
#    alt_text = "�д��ѫH�c",
#    contents = BubbleContainer(
#        direction = "ltr",
#        body = BoxComponent(
#          layout = "vertical",
#          contents = [
#          TextComponent(
#              text = "�д��ѥi�H�p���z���q�l�H�c",
#              size = "lg",
#              align = "center",
#              weight = "bold"
#              )
#          ]
#        )
#    )
#)


def summary(data):
    if data[12] == '�L':
        act = None
        col = "#141414"
    else:
        act = URIAction(uri = f"{data[12]}")
        col = "#229C8F"
        
    sum = FlexSendMessage(
        alt_text = "�нT�{�}�θ�T",
        contents = BubbleContainer(
            direction = "ltr",
            header = BoxComponent(
              layout = "vertical",
              contents = [
              TextComponent(
                  text = "�нT�{�}�θ�T�G",
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
                        layout = "horizontal",
                        contents = [
                            TextComponent(
                                text = f"���������G{data[1]}",
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
                                    label = "�קﬡ������",
                                    data = "�ק�}��_activity_type",
                                    display_text = "�קﬡ������"
                                )
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
                                text = "�ק�",
                                size = "md",
                                align = "end",
                                gravity = "top",
                                weight = "bold",
                                action = PostbackAction(
                                    label = "�קﬡ�ʦW��",
                                    data = "�ק�}��_activity_name",
                                    display_text = "�קﬡ�ʦW��"
                                )
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
                            ),
                            SeparatorComponent(
                                margin = "lg"
                            )
                        ]
                    ),BoxComponent(
                        layout = "horizontal",
                        contents = [
                            TextComponent(
                                text = "�ק�",
                                size = "md",
                                align = "end",
                                gravity = "top",
                                weight = "bold",
                                action = PostbackAction(
                                    label = "�קﬡ�ʮɶ�",
                                    data = "�ק�}��_activity_date",
                                    display_text = "�קﬡ�ʮɶ�"
                                )
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
                                    label = "�קﬡ�ʦa�I",
                                    data = "�ק�}��_location_tittle",
                                    display_text = "�קﬡ�ʦa�I"
                                )                            )
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
                                    label = "�קﬡ�ʤH��",
                                    data = "�ק�}��_people",
                                    display_text = "�קﬡ�ʤH��"
                                )
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
                                    label = "�קﬡ�ʶO��",
                                    data = "�ק�}��_cost",
                                    display_text = "�קﬡ�ʶO��"
                                )
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
                                    label = "�ק���W�I���",
                                    data = "�ק�}��_due_date",
                                    display_text = "�ק���W�I���"
                                )
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
                                    label = "�קﬡ�ʱԭz",
                                    data = "�ק�}��_description",
                                    display_text = "�קﬡ�ʱԭz"
                                )
                            )
                        ]
                    ),
                    BoxComponent(
                        layout = "horizontal",
                        contents = [
                            TextComponent(
                                text = f"���ʷӤ��G{data[12]}",
                                size = "md",
                                flex = 10,
                                align = "start",
                                action= act,
                                wrap = True,
                                color = f"{col}"
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
                                    label = "�קﬡ�ʷӤ�",
                                    data = "�ק�}��_photo",
                                    display_text = "�קﬡ�ʷӤ�"
                                )
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
                                    label = "�ק�D���m�W",
                                    data = "�ק�}��_name",
                                    display_text = "�ק�D���m�W"
                                )
                            )
                        ]
                    ),
                    BoxComponent(
                        layout = "horizontal",
                        contents = [
                            TextComponent(
                                text = f"�D���q�ܡG{data[14]}",
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
                                    label = "�ק�D���q��",
                                    data = "�ק�}��_phone",
                                    display_text = "�ק�D���q��"
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
                            label = "�T�{�}��",
                            data = "�T�{�}��",
                            display_text = "�T�{�}��"
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
                            label = "�����}��",
                            data = "~cancel",
                            display_text = "�����}��"
                        )
                    )
                ]
            )
        )
    )
    return sum
