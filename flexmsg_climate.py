def climate():

    msg =  BubbleContainer(
        header = BoxComponent(
            layout = "vertical",
            contents = TextComponent(
                text = "天氣預報",
                size = "lg"
            ),
            background_color = "#A7D5E1"
        ),
        body = BoxComponent(
            layout = "vertical",
            contents = [
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
                        BoxComponent(
                           layout = "vertical",
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
                                           size = "sm",
                                           flex = 1,
                                           align = "end"
                                       ),
                                       TextComponent(
                                           text = "晴時多雲",
                                           wrap = True,                                    
                                           size = "3xl",
                                           flex = 5,
                                           align = "end"
                                       ),
                                   ]
                               ),
                               BoxComponent(
                                   layout = "baseline",
                                   spacing = "sm",
                                   flex = 4,
                                   contents = [
                                       ImageComponent(
                                           url = "",
                                           size = "5xl"
                                       )
                                   ]

                               )

                           ] 
                        )
                    ]
                ),        
                BoxComponent(
                    layout = "horizontal",
                    contents = [
                        BoxComponent(
                            layout = "vertical",
                            flex = 3,
                            contents = [
                                TextComponent(
                                    text = "16C",
                                    size = "3xl"
                                )
                            ]
                        ),
                        BoxComponent(
                            layout = "vertical",
                            flex = 7,
                            contents = [
                                TextComponent(
                                    text = "最高25Ｃ 最低12Ｃ",
                                    offset_top = "xxl"
                                )
                            ]
                        )
                    ]
                )
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
                )
            ]
        )
    )

    return msg

