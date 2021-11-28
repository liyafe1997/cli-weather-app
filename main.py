import gzip
import json
from select import select
import requests
from datetime import datetime
import time
import curses


def DownloadCityData(url):
    print("Fetching City Data...")
    city_data = json.loads(gzip.decompress(requests.get(url).content))
    print("City data loaded.")
    return city_data


def ShowCurrentWeather(stdscr, selected_city):
    stdscr.erase()
    stdscr.refresh()
    #print(selected_city)
    stdscr.addstr(selected_city["name"] + " Current Weather:\n")
    json_data = json.loads(requests.get("https://api.openweathermap.org/data/2.5/weather?id=" + str(selected_city["id"]) + "&appid=93c4fc843f2189f3232b27952027013b&units=metric").content)
    temp_min = str(int(float(json_data["main"]["temp_min"])))
    temp_max = str(int(float(json_data["main"]["temp_max"])))
    humidity = str(int(float(json_data["main"]["humidity"])))
    weather = ""
    for j in json_data["weather"]:
        if (weather != ""):
            weather = weather + " and "
        weather += j["main"]
    try:
        stdscr.addstr("  " + weather + ", " + temp_min + "℃  to " + temp_max + "℃ ," + "  Humidity:" + humidity + "%")
        stdscr.addstr("\n")
    except:
        pass
    c = stdscr.getch()


def ShowForecast(stdscr, selected_city):
    stdscr.erase()
    stdscr.refresh()
    #print(selected_city)
    json_data = json.loads(requests.get("https://api.openweathermap.org/data/2.5/forecast?id=" + str(selected_city["id"]) + "&appid=93c4fc843f2189f3232b27952027013b&units=metric").content)
    for i in json_data["list"]:
        date = datetime.fromtimestamp(i["dt"]).strftime("%Y-%m-%d")
        temp_min = str(int(float(i["main"]["temp_min"])))
        temp_max = str(int(float(i["main"]["temp_max"])))
        humidity = str(int(float(i["main"]["humidity"])))
        weather = ""
        for j in i["weather"]:
            if (weather != ""):
                weather = weather + " and "
            weather += j["main"]
        try:
            stdscr.addstr(date + ": " + weather + ", " + temp_min + "℃  to " + temp_max + "℃," + "  Humidity:" + humidity + "%")
            stdscr.addstr("\n")
        except:
            pass

    stdscr.refresh()
    c = stdscr.getch()
    stdscr.leaveok(True)
    while True:
        if c == curses.KEY_DOWN:
            stdscr.move(0, 0)
            #stdscr.refresh()
        elif c == curses.KEY_UP:
            stdscr.move(10, 5)
            #stdscr.refresh()
    stdscr.clear()
    stdscr.refresh()


def SearchingMenu(stdscr, city_data):
    curses.use_default_colors()
    stdscr.scrollok(True)
    #stdscr.idlok(True)
    #stdscr.keypad(True)
    input_string = ""
    input_string_before_cursor = ""
    input_string_after_cursor = ""
    c = 0
    selected_index = 0
    selected_city = []
    while True:
        city_list = []
        city_list_count = 0
        too_many_result_flag = 0
        stdscr.erase()

        # Pages
        max_x, max_y = stdscr.getmaxyx()
        stdscr.addstr("max_x=" + str(max_x) + " max_y=" + str(max_y) + "\n")
        
        # Search
        stdscr.addstr("Search for City: " + input_string_before_cursor + "_" + input_string_after_cursor)
        stdscr.addstr("\n")
        #stdscr.addstr("InputKey:" + str(c) + "\n")
        input_string = input_string_before_cursor + input_string_after_cursor
        if (input_string != ""):
            stdscr.addstr("City List:\n")
            for i in city_data:
                if input_string.upper() in i["name"].upper():
                    if (city_list_count < 10):
                        city_list.append(i)
                        city_list_count += 1
                    else:
                        too_many_result_flag = 1
            if (too_many_result_flag):
                stdscr.addstr("  Too many result! Only show first 10 result. Please enter more details.\n")
            if (len(city_list) != 0):
                for i in range(0, len(city_list)):
                    try:
                        if (selected_index == i):
                            stdscr.addstr("  [->]")
                            selected_city = city_list[i]
                        else:
                            stdscr.addstr("  [  ]")
                        stdscr.addstr(str(i) + "." + city_list[i]["name"] + "\n")
                    except:
                        pass

        c = stdscr.getch()
        if ((c >= 33 and c <= 126) or (c >= 128 and c <= 254)):
            input_string_before_cursor += chr(c)
            selected_index = 0
        elif (c == curses.KEY_BACKSPACE or c == 127):
            input_string_before_cursor = input_string_before_cursor[:-1]
            selected_index = 0
        elif (c == 330):
            input_string_after_cursor = input_string_after_cursor[1:]
        elif (c == curses.KEY_UP and selected_index > 0):
            selected_index -= 1
        elif (c == curses.KEY_DOWN and selected_index < len(city_list) - 1):
            selected_index += 1
        elif (c == curses.KEY_RIGHT):
            if (input_string_after_cursor != ""):
                input_string_before_cursor += input_string_after_cursor[0]
                input_string_after_cursor = input_string_after_cursor[1:]
            pass
        elif (c == curses.KEY_LEFT):
            if (input_string_before_cursor != ""):
                input_string_after_cursor = input_string_before_cursor[-1] + input_string_after_cursor
                input_string_before_cursor = input_string_before_cursor[:-1]
            pass
        elif (c == curses.KEY_ENTER or c == 10):
            print(selected_city)
            ShowCurrentWeather(stdscr, selected_city)
        stdscr.addstr(input_string, curses.A_UNDERLINE)

    stdscr.getch()


if __name__ == "__main__":
    #city_data = DownloadCityData("http://bulk.openweathermap.org/sample/city.list.json.gz")
    city_data = DownloadCityData("http://127.0.0.1:8000/city.list.json.gz")
    selected_city = curses.wrapper(SearchingMenu, city_data)
    pass
