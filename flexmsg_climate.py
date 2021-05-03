from linebot.models import *
from flask import url_for

def climate(activity_date, county, district, rain, weather, temperature_avg, temperature_max, temperature_min, humidity, wind_d, wind_v, uvi):
    rain_prob = f"降雨機率:{rain}%" if rain != " " else "無降雨機率資料"
    weather_size = "xl" if len(weather) > 4 else "31px"

    if "晴" in weather and "雨" in weather:
        image = "https://i.imgur.com/jM4qYAq.png"
    elif "雷雨" in weather:
        image = "https://i.imgur.com/tEXBJwC.png"  
    elif "雨" in weather:
        image = "https://i.imgur.com/NULZt0V.png"
    elif "晴" in weather and ("陰" in weather or "多雲" in weather):
        image = "https://i.imgur.com/M0N0JSk.png"
    elif "晴" in weather:
        image = "https://i.imgur.com/Rjogm0N.png"
    else:
        image = "https://i.imgur.com/BoseTDT.png"

    bubble = BubbleContainer(
        size = "kilo",
        direction = "ltr",
        header = BoxComponent(
            layout = "vertical",
            background_color = "#A7D5E1",
            contents = [
                TextComponent(
                    text = "天氣預報",
                    size = "lg",
                    align = "start",
                    color = "#ffffff"
                )
            ]
        ),
        body = BoxComponent(
            layout = "vertical",
            contents = [
                BoxComponent(
                    layout = "horizontal",
                    spacing = "xl",
                    contents = [

                        BoxComponent(
                            layout = "vertical",
                            flex = 6,
                            contents = [
                                TextComponent(
                                    text = f"{county} {district}",
                                    color = "#aaaaaa",
                                    size = "lg",
                                    flex = 1,
                                    align = "start" #offset_top = "5px"
                                ),
                                TextComponent(
                                    text = rain_prob,
                                    color = "#aaaaaa",
                                    size = "md",
                                    flex = 1,
                                    align = "end",
                                    offset_top = "5px"
                                ),
                                TextComponent(
                                    text = weather,
                                    wrap = True,                                    
                                    size = weather_size,
                                    flex = 3,
                                    align = "end",
                                    offset_top = "sm"
                                ),
                            ]
                        ),
                        BoxComponent(
                            layout = "vertical",
                            spacing = "sm",
                            flex = 4,
                            contents = [
                                ImageComponent(
                                    url = image,
                                    size = "5xl"
                                )
                            ]
                        )
                    ] 
                ),
                BoxComponent(
                    layout = "horizontal",
                    margin = "md",
                    contents = [
                        TextComponent(
                            flex = 3,
                            text = f" {temperature_avg}ºC",
                            size = "xxl"
                        ),
                        TextComponent(
                            flex = 6,
                            text = f"最高{temperature_max}ºC  最低{temperature_min}ºＣ",
                            offset_top = "lg"
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
                            text = f"{activity_date}",
                            color = "#8c8c8c",
                            margin = "xl",
                            size = "md" 
                        ),
                        TextComponent(
                            text = f"相對濕度: {humidity} %",
                            color = "#8c8c8c",
                            margin = "sm",
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

def no_climate():

    bubble = BubbleContainer(
        direction = "ltr",
        body = BoxComponent(
            size = "xs",
            layout = "vertical",
            spacing = "md",
            contents = [
                TextComponent(
                    text = "僅提供未來一週內的天氣預報",
                    size = "lg",
                    weight = "bold",
                    color = "#AAAAAA"
                )
            ]
        )
    )

    msg = FlexSendMessage(
        alt_text = "僅提供一週內的天氣預報！",
        contents = bubble
    )

    return msg

def no_data():

    bubble = BubbleContainer(
        direction = "ltr",
        body = BoxComponent(
            size = "xs",
            layout = "vertical",
            spacing = "md",
            contents = [
                TextComponent(
                    text = "無資料",
                    size = "lg",
                    weight = "bold",
                    color = "#AAAAAA"
                )
            ]
        )
    )

    msg = FlexSendMessage(
        alt_text = "無資料",
        contents = bubble
    )

    return msg