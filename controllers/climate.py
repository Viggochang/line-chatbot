import datetime as dt
import requests
from models import CallDatabase
from templates import flexmsg_climate

def location_datetime(activity_id):
    condition = [f"id = {activity_id}"]
    location_datetime = CallDatabase.get_data("activity", ["location_longitude", "location_latitude", "activity_date", "activity_time"], condition = condition, all_data = False)
    return location_datetime

def geo_data(mapbox_key, location_longitude, location_latitude):
    geo_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{location_longitude},{location_latitude}.json"
    my_params = {"language": "zh-tw", "access_token": mapbox_key}
    re_mapbox = requests.get(geo_url, params = my_params)
    county = re_mapbox.json()["features"][0]["context"][-2]["text"]
    district = re_mapbox.json()["features"][0]["context"][-3]["text"]
    print(county, district)
    return county, district

def climate(climate_key, county, district, activity_date, activity_time):
    try:
        # climate_data
        county_code = {'宜蘭縣': 'F-D0047-003', '桃園市': 'F-D0047-007', '新竹縣': 'F-D0047-011', '苗栗縣': 'F-D0047-015', '彰化縣': 'F-D0047-019', '南投縣': 'F-D0047-023', '雲林縣': 'F-D0047-027', '嘉義縣': 'F-D0047-031', '屏東縣': 'F-D0047-035', '臺東縣': 'F-D0047-039', '花蓮縣': 'F-D0047-043', '澎湖縣': 'F-D0047-047', '基隆市': 'F-D0047-051', '新竹市': 'F-D0047-055', '嘉義市': 'F-D0047-059', '臺北市': 'F-D0047-063', '高雄市': 'F-D0047-067', '新北市': 'F-D0047-071', '臺中市': 'F-D0047-075', '臺南市': 'F-D0047-079', '連江縣': 'F-D0047-083', '金門縣': 'F-D0047-087'}
        climate_url = f"https://opendata.cwb.gov.tw/api/v1/rest/datastore/{county_code.get(county)}"
        my_params = {"Authorization": climate_key, "locationName": district}

        re_climate = requests.get(climate_url, params = my_params).json()
        weather_element = re_climate["records"]["locations"][0]["location"][0]["weatherElement"]
        UVI = weather_element.pop(9)

        start_time = dt.datetime.strptime(weather_element[0]["time"][0]["startTime"], "%Y-%m-%d %H:%M:%S")
        dt_list = [start_time] + [dt.datetime.strptime(time["endTime"], "%Y-%m-%d %H:%M:%S") for time in weather_element[0]["time"]]
        activity_dt = dt.datetime.strptime(str(activity_date) + str(activity_time), "%Y-%m-%d%H:%M:%S")
        i = 0
        while i < len(dt_list) - 1:
            if dt_list[i] <= activity_dt < dt_list[i+1]:
                break
            else:
                i += 1
        print(i)

        if i == len(dt_list) - 1:
            print("僅提供一週內的天氣預報！")
            return flexmsg_climate.no_climate()

        else:
            climate_data = {item["description"]: list(item["time"][i]["elementValue"][0].values()) for item in weather_element}
            UVI = {item["startTime"].split()[0]:[[row["value"], row["measures"]] for row in item["elementValue"]] for item in UVI["time"]}
            uvi = [row[0] for row in UVI.get(str(activity_date), [])]
            print(activity_dt, weather_element[0]["time"][i], climate_data, end = "\n")
            
            climate_lst = ["12小時降雨機率", "天氣現象", "平均溫度", "最高溫度", "最低溫度", "平均相對濕度", "風向", "最大風速"]
            climate_info = [climate_data[item][0] for item in climate_lst] + [uvi]
            return flexmsg_climate.climate(activity_date, county, district, climate_info)
    except:
        return flexmsg_climate.no_data()
