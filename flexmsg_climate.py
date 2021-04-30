from linebot.models import *

def climate(rain, weather, temperature_avg, temperature_max, temperature_min, humidity, wind_d, wind_v, uvi):
    rain_prob = f"降雨機率:{rain}%" if rain else "目前無降雨機率資料"

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
                                    text = rain_prob,
                                    color = "#aaaaaa",
                                    size = "md",
                                    flex = 1,
                                    align = "end",
                                    offset_top = "25px"
                                ),
                                TextComponent(
                                    text = weather,
                                    wrap = True,                                    
                                    size = "xxl",
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
                            flex = 4,
                            text = f"{temperature_avg}ºC",
                            size = "3xl"
                        ),
                        TextComponent(
                            flex = 6,
                            text = f"最高{temperature_max}ºC 最低{temperature_min}ºＣ",
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
                            text = f"相對濕度: {humidity} %",
                            color = "#8c8c8c",
                            margin = "xl",
                            size = "sm" 
                        ),
                        TextComponent(
                            text = f"紫外線指數: {uvi[0]} ({uvi[1]})",
                            color = "#8c8c8c",
                            margin = "sm",
                            size = "sm" 
                        ),
                        TextComponent(
                            text = f"風向: {wind_d}",
                            color = "#8c8c8c",
                            margin = "sm",
                            size = "sm" 
                        ),
                        TextComponent(
                            text = f"最大風速: {wind_v} m/s",
                            color = "#8c8c8c",
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