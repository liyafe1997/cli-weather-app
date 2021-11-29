import gzip
import json
import requests
from datetime import datetime
import curses


def DownloadCityData(url):
    print("Fetching City Data...")
    try:
        city_data = json.loads(gzip.decompress(requests.get(url).content))
        print("City data loaded.")
    except:
        print("Fetch City Data Failed! Please check your internet connection.")
        exit(-1)
    return city_data


def ShowCurrentWeather(stdscr, selected_city):
    stdscr.erase()
    try:
        stdscr.addstr("Loading data from server....\n")
        json_data = json.loads(requests.get("https://api.openweathermap.org/data/2.5/weather?id=" + str(selected_city["id"]) + "&appid=93c4fc843f2189f3232b27952027013b&units=metric").content)
    except:
        stdscr.addstr("Load data failed! Unable to connect to server.\nPress any key to back to menu.")
        stdscr.getch()
        return

    temp_min = str(int(float(json_data["main"]["temp_min"])))
    temp_max = str(int(float(json_data["main"]["temp_max"])))
    humidity = str(int(float(json_data["main"]["humidity"])))
    weather = ""
    for j in json_data["weather"]:
        if (weather != ""):
            weather = weather + " and "
        weather += j["main"]

    #Menu options
    menu_list = ["Weather Forecast in 5 Days", "Air Pollution Information", "Back"]
    selected_index = 0
    current_page = 0
    max_x, max_y = stdscr.getmaxyx()
    while True:
        stdscr.erase()
        #Display current weather
        try:
            stdscr.addstr("[" + selected_city["name"] + "] Current Weather:\n")
            stdscr.addstr("  " + weather + ", " + temp_min + "℃  to " + temp_max + "℃ ," + "  Humidity:" + humidity + "%")
            stdscr.addstr("\n")
            stdscr.addstr("Please choose an option:\n")
        except:
            pass
        # Page the result
        max_lines = max_x - 4
        try:
            pages = int(len(menu_list) / max_lines)
        except:
            pass
        new_max_x, new_max_y = stdscr.getmaxyx()
        if (new_max_x != max_x):
            #reflash page when terminal size be changed
            current_page = 0
            selected_index = 0
            max_x = new_max_x
            max_y = new_max_y
        #display menu
        if (len(menu_list) != 0):
            for i in range(0, len(menu_list)):
                if (int(i / max_lines) == current_page):
                    try:
                        if (selected_index == i):
                            stdscr.addstr("  [->]")
                        else:
                            stdscr.addstr("  [  ]")
                        stdscr.addstr(str(i + 1) + "." + menu_list[i] + "\n")
                    except:
                        pass
        c = stdscr.getch()
        if (c == curses.KEY_UP and selected_index > 0):
            # switch page
            if ((selected_index + 1) % max_lines == 1):
                if (current_page > 0):
                    current_page -= 1
            selected_index -= 1
        elif (c == curses.KEY_DOWN and selected_index < len(menu_list) - 1):
            selected_index += 1
            # switch page
            if (selected_index % max_lines == 0):
                current_page += 1
        elif (c == curses.KEY_ENTER or c == 10):
            if (selected_index == 0):
                ShowForecast(stdscr, selected_city)
            if (selected_index == 1):
                ShowAirPullution(stdscr, selected_city)
                pass
            if (selected_index == 2):
                return
        elif (c == 27):
            return


def ShowAirPullution(stdscr, selected_city):
    stdscr.erase()
    try:
        stdscr.addstr("Loading data from server....\n")
        json_data = json.loads(
            requests.get("https://api.openweathermap.org/data/2.5/air_pollution?lat=" + str(selected_city["coord"]["lat"]) + "&lon=" + str(selected_city["coord"]["lon"]) +
                         "&appid=93c4fc843f2189f3232b27952027013b&units=metric").content)
    except:
        stdscr.addstr("Load data failed! Unable to connect to server.\nPress any key to back to menu.")
        stdscr.getch()
        return

    info_list = []
    for i in json_data["list"]:
        date = datetime.fromtimestamp(i["dt"]).strftime("%Y-%m-%d %H:%M")
        aqi = str(float(i["main"]["aqi"]))
        no = str(float(i["components"]["no"]))
        no2 = str(float(i["components"]["no2"]))
        o3 = str(float(i["components"]["o3"]))
        so2 = str(float(i["components"]["so2"]))
        pm2_5 = str(float(i["components"]["pm2_5"]))
        pm10 = str(float(i["components"]["pm10"]))
        co = str(float(i["components"]["co"]))
        nh3 = str(float(i["components"]["nh3"]))

        info_list.append(date + ": ")
        info_list.append("    AQI: " + aqi)
        info_list.append("    NO: " + no)
        info_list.append("    NO₂: " + no2)
        info_list.append("    O₃: " + o3)
        info_list.append("    SO₂: " + so2)
        info_list.append("    PM2.5: " + pm2_5)
        info_list.append("    PM10: " + pm10)
        info_list.append("    CO: " + co)
        info_list.append("    NH₃: " + nh3)

    #Menu options
    current_page = 0
    max_x, max_y = stdscr.getmaxyx()
    while True:
        stdscr.erase()

        # Page the result
        max_lines = max_x - 4
        try:
            pages = int(len(info_list) / max_lines)
        except:
            pass
        new_max_x, new_max_y = stdscr.getmaxyx()

        #Display info string
        try:
            stdscr.addstr("[" + selected_city["name"] + "] Air Pullution Info:\n")
            stdscr.addstr("Page " + str(current_page + 1) + "/" + str(pages + 1) + ". Press ↑ / ↓ key for switch page, Enter or ESC for return to menu.\n")
        except:
            pass

        if (new_max_x != max_x):
            #reflash page when terminal size be changed
            current_page = 0
            max_x = new_max_x
            max_y = new_max_y
        #display menu
        if (len(info_list) != 0):
            for i in range(0, len(info_list)):
                if (int(i / max_lines) == current_page):
                    try:
                        stdscr.addstr("  " + info_list[i] + "\n")
                    except:
                        pass
        c = stdscr.getch()
        if (c == curses.KEY_UP):
            # switch page
            if (current_page > 0):
                current_page -= 1
        elif (c == curses.KEY_DOWN):
            # switch page
            if (current_page + 1 <= pages):
                current_page += 1
        elif (c == curses.KEY_ENTER or c == 10 or C == 27):
            return


def ShowForecast(stdscr, selected_city):
    stdscr.erase()
    try:
        stdscr.addstr("Loading data from server....\n")
        json_data = json.loads(requests.get("https://api.openweathermap.org/data/2.5/forecast?id=" + str(selected_city["id"]) + "&appid=93c4fc843f2189f3232b27952027013b&units=metric").content)
    except:
        stdscr.addstr("Load data failed! Unable to connect to server.\nPress any key to back to menu.")
        stdscr.getch()
        return
    info_list = []
    for i in json_data["list"]:
        date = datetime.fromtimestamp(i["dt"]).strftime("%Y-%m-%d %H:%M")
        temp_min = str(int(float(i["main"]["temp_min"])))
        temp_max = str(int(float(i["main"]["temp_max"])))
        humidity = str(int(float(i["main"]["humidity"])))
        weather = ""
        for j in i["weather"]:
            if (weather != ""):
                weather = weather + " and "
            weather += j["main"]
            info_list.append(date + ": " + weather + ", " + temp_min + "℃  to " + temp_max + "℃," + "  Humidity:" + humidity + "%")

    #Menu options
    current_page = 0
    max_x, max_y = stdscr.getmaxyx()
    while True:
        stdscr.erase()

        # Page the result
        max_lines = max_x - 4
        try:
            pages = int(len(info_list) / max_lines)
        except:
            pass
        new_max_x, new_max_y = stdscr.getmaxyx()

        #Display info string
        try:
            stdscr.addstr("[" + selected_city["name"] + "] 5 days forecast:\n")
            stdscr.addstr("Page " + str(current_page + 1) + "/" + str(pages + 1) + ". Press ↑ / ↓ key for switch page, Enter or ESC for return to menu.\n")
        except:
            pass

        if (new_max_x != max_x):
            #reflash page when terminal size be changed
            current_page = 0
            max_x = new_max_x
            max_y = new_max_y
        #display menu
        if (len(info_list) != 0):
            for i in range(0, len(info_list)):
                if (int(i / max_lines) == current_page):
                    try:
                        stdscr.addstr("  " + info_list[i] + "\n")
                    except:
                        pass
        #Deal with key press
        c = stdscr.getch()
        if (c == curses.KEY_UP):
            # switch page
            if (current_page > 0):
                current_page -= 1
        elif (c == curses.KEY_DOWN):
            # switch page
            if (current_page + 1 <= pages):
                current_page += 1
        elif (c == curses.KEY_ENTER or c == 10 or c == 27):
            return


def SearchingMenu(stdscr, city_data):
    curses.use_default_colors()
    stdscr.scrollok(True)

    #input string init
    input_string = ""
    input_string_before_cursor = ""
    input_string_after_cursor = ""
    selected_city = []

    # menu parameters
    selected_index = 0
    current_page = 0
    max_x, max_y = stdscr.getmaxyx()
    while True:
        city_list = []
        city_list_count = 0
        too_many_result_flag = 0
        stdscr.erase()

        # Search
        stdscr.addstr("Search for City: " + input_string_before_cursor + "_" + input_string_after_cursor)
        stdscr.addstr("\n")
        #stdscr.addstr("InputKey:" + str(c) + "\n")
        input_string = input_string_before_cursor + input_string_after_cursor
        if (input_string != ""):
            stdscr.addstr("City List:\n")
            for i in city_data:
                if input_string.upper() in i["name"].upper():
                    if (city_list_count < 20):
                        city_list.append(i)
                        city_list_count += 1
                    else:
                        too_many_result_flag = 1
            if (too_many_result_flag):
                stdscr.addstr("  Too many result! Only show first 20 result. Please enter more details.\n")

            # Page the result
            max_lines = max_x - 4
            try:
                pages = int(len(city_list) / max_lines)
            except:
                pass
            new_max_x, new_max_y = stdscr.getmaxyx()
            if (new_max_x != max_x):
                #reflash page when terminal size be changed
                current_page = 0
                selected_index = 0
                max_x = new_max_x
                max_y = new_max_y

            #display menu
            if (len(city_list) != 0):
                for i in range(0, len(city_list)):
                    #only display current page
                    if (int(i / max_lines) == current_page):
                        try:
                            #Display each menu item
                            if (selected_index == i):
                                stdscr.addstr("  [->]")
                                selected_city = city_list[i]
                            else:
                                stdscr.addstr("  [  ]")
                            stdscr.addstr(str(i + 1) + "." + city_list[i]["name"] + "\n")
                        except:
                            pass
        #Deal with key press
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
            # switch page
            #If the first item be selected on current page will switch to last page
            if ((selected_index + 1) % max_lines == 1):
                if (current_page > 0):
                    current_page -= 1
            selected_index -= 1
        elif (c == curses.KEY_DOWN and selected_index < len(city_list) - 1):
            selected_index += 1
            # switch page
            #If the last item be selected on current page will switch to next page
            if (selected_index % max_lines == 0):
                current_page += 1

        elif (c == curses.KEY_RIGHT):
            if (input_string_after_cursor != ""):
                input_string_before_cursor += input_string_after_cursor[0]
                input_string_after_cursor = input_string_after_cursor[1:]
            pass
        elif (c == curses.KEY_LEFT):
            if (input_string_before_cursor != ""):
                input_string_after_cursor = input_string_before_cursor[-1] + \
                    input_string_after_cursor
                input_string_before_cursor = input_string_before_cursor[:-1]
            pass
        elif (c == 27):
            exit()
        elif (c == curses.KEY_ENTER or c == 10):
            ShowCurrentWeather(stdscr, selected_city)


if __name__ == "__main__":
    city_data = DownloadCityData("http://bulk.openweathermap.org/sample/city.list.json.gz")
    #city_data = DownloadCityData("http://127.0.0.1:8000/city.list.json.gz")
    selected_city = curses.wrapper(SearchingMenu, city_data)
    pass
