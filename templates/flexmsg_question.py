from linebot.models import *
columns = ["activity_type", "activity_name", "activity_date", "activity_time", 
            "location_title", "location_latitude", "location_longitude", "people", "cost", "due_date", 
            "description", "photo", "name", "phone"]
columns_text = ["活動類型", "活動名稱", "活動時間", "活動時間",
            "活動地點", "活動地點", "活動地點", "活動人數", "活動費用", "報名截止日期", 
            "活動敘述", "活動相片", "姓名", "電話"]

def flex_header(text):
    flex_header = BoxComponent(
        layout = "vertical",
        height = "63px",
        contents = [
            TextComponent(
                text = text, 
                weight = "bold", 
                size = "lg", 
                align = "center"
            )
        ]
    )
    return flex_header

def flex_body(text):
    flex_body = BoxComponent(
        layout = "vertical",
        contents = [
            TextComponent(
                text = f"請告訴我{text}" if text != "活動相片" else "請上傳一張相片",
                size = "md", 
                color = "#666666"
            )
        ]
    )
    return flex_body

def prog_rate(col, q_count):   
    if q_count == 2:
        progress_i = {"name": 1, "phone": 2}
    else:    
        progress_i = {"activity_name": 1, "activity_date": 2, "location_title":3, "people": 4, "cost": 5, "name": 6, "phone": 7}
    i = progress_i.get(col, 0)
    
    prog_rate = BoxComponent(
        layout = "vertical",
        margin = "md",
        height = "45px",
        contents = [
            TextComponent(
                text = f"{i} / {q_count} ", 
                weight = "bold", 
                size = "md"
            ),
            BoxComponent(
                layout = "vertical", 
                margin = "md", 
                width = f"{int(i / q_count * 100 + 0.5 )}%",
                background_color = "#3DE1D0",
                height = "6px"
            )
        ]
    )
    return prog_rate 

def button(col, activity_date = None):
    if col == "activity_date":
        action = DatetimePickerAction(
            label = "點我選時間",
            data = "回覆活動時間",
            mode = "datetime"
        )
        
    elif col == "location_title":
        action = URIAction(
            label = "點我選地點",
            uri = "https://line.me/R/nv/location"
        )
        
    elif col == "due_date":
        action = DatetimePickerAction(
            label = "點我選時間",
            data = "回覆報名截止時間",
            mode = "date",
            max = str(activity_date)
        )

    button = ButtonComponent(
        action = action,
        height = "sm",
        margin = "md",
        style = "primary",
        color = "#A7D5E1",
        gravity = "bottom"
    )
    return button


def question(col, progress = 0, activity_date = None):

    text = columns_text[columns.index(col)]

    footer_contents = []
    if progress:
        footer_contents.append(prog_rate(col, progress))
    if col in ["activity_date", "location_title", "due_date"]:
        footer_contents.append(button(col, activity_date))

    question = FlexSendMessage(
        alt_text = f"請告訴我{text}",
        contents = BubbleContainer(
            direction = "ltr",
            header = flex_header(text),
            body = flex_body(text),
            footer = BoxComponent(
                layout = "vertical",
                margin = "md",
                contents = footer_contents
            )
        )
    )
    return question
    