from linebot.models import *

def x():
    bubble = BubbleContainer(
        header = BoxComponent(
            layout = "vertical",
            background_color = "#A7D5E1",
            contents = [
                TextComponent(
                    text = "天氣預報",
                    size = "xl"
                )
            ]
        ),
        body = BoxComponent(
            layout = "vertical",
            contents = [
                BoxComponent(
                    layout = "horizontal",
                    margin = "lg",
                    spacing = "xl",
                    contents = [
                        BoxComponent(
                            layout = "vertical",
                            flex = 6,
                            contents = [
                                TextComponent(
                                    text = "降雨機率:15%",
                                    color = "#aaaaaa",
                                    size = "md",
                                    flex = 1,
                                    align = "end",
                                    offset_top = "25px"
                                ),
                                TextComponent(
                                    text = "晴天多雲",
                                    wrap = True,                                    
                                    size = "3xl",
                                    flex = 1,
                                    align = "end",
                                    offset_top = "lg"
                                ),
                            ]
                        ),
                        BoxComponent(
                            layout = "vertical",
                            spacing = "sm",
                            flex = 4,
                            contents = [
                                ImageComponent(
                                    # 待改
                                    url = "https://uploadfile.huiyi8.com/2016/0620/20160620120418789.jpg",
                                    size = "5xl"
                                )
                            ]
                        )
                    ] 
                ),
                BoxComponent(
                    layout = "horizontal",
                    contents = [
                        TextComponent(
                            flex = 3,
                            text = "16C",
                            size = "3xl"
                        ),
                        TextComponent(
                            flex = 7,
                            text = "最高25Ｃ 最低12Ｃ",
                            offset_top = "xxl"
                        )
                    ]
                ),
                BoxComponent(
                    layout = "vertical",
                    contents = [
                        SeparatorComponent(
                            margin = "xs"
                        )
                    ]
                ),
                BoxComponent(
                    layout = "vertical",
                    contents = [
                        TextComponent(
                            text = "相對濕度: 10%",
                            margin = "xl",
                            size = "sm" 
                        ),
                        TextComponent(
                            text = "紫外線等級: 過量級",
                            margin = "sm",
                            size = "sm" 
                        ),
                        TextComponent(
                            text = "風向: 偏西風%",
                            margin = "sm",
                            size = "sm" 
                        ),
                        TextComponent(
                            text = "最大風速: 5 m/s",
                            margin = "sm",
                            size = "sm" 
                        )
                    ]
                ),
            ]
        )
    )

    msg = FlexSendMessage(
        alt_text = "天氣預報",
        contents = bubble
    )

    return msg        