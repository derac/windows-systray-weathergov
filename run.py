import json, webbrowser, os
import requests

import tkinter as tk
from time import sleep
from tkinter import simpledialog, colorchooser

from infi.systray import SysTrayIcon
from PIL import Image, ImageFont, ImageDraw, ImageEnhance

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Change the working directory to the script directory
os.chdir(script_dir)

# open config
with open("config.json") as fh:
    config = json.loads(fh.read())

# create image
def write_ico(text="10"):
    with open("config.json") as fh:
        config = json.loads(fh.read())
    W = 256
    H = 256
    h = 230 if len(text)<=2 else 152
    r,g,b = (int(c) for c  in config["color"].split(","))
    text_color = (r,g,b,255)
    background = (0,0,0,0)
    font = ImageFont.truetype("Roboto-Black.ttf",size=h)
    image = Image.new(mode="RGBA", size=(W, H),color= background)
    draw = ImageDraw.Draw(image)
    w = draw.textlength(text, font=font)
    draw.text(((W-w)/2,(H-h)/2), text, fill = text_color, font = font)
    image.save("icon.ico")

def configure_city_state(systray):
    # open config
    with open("config.json") as fh:
        config = json.loads(fh.read())
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    city_state = simpledialog.askstring("Configure City", "Please enter your city and state - i.e. : \"San Marcos, Texas\"")
    response = requests.get(f"https://nominatim.openstreetmap.org/search?q={city_state}&format=jsonv2", headers = {'User-Agent': 'Weather app configuration'})
    city_json = json.loads(response.content)[0]
    lat = round(float(city_json["lat"]),2)
    lon = round(float(city_json["lon"]),2)
    response = requests.get(f"https://api.weather.gov/points/{lat},{lon}")
    station_info = json.loads(response.content)
    url = station_info["properties"]["forecastHourly"]
    config = {
        "lat": lat,
        "lon": lon,
        "city": city_json["name"],
        "url": url,
        "color": config["color"]
    }
    # write config
    with open("config.json", "w") as fh:
        fh.write(json.dumps(config))
    # update temp
    # get current temp
    response = requests.get(config["url"])
    json_response = json.loads(response.content)
    temp = json_response["properties"]["periods"][0]["temperature"]

    write_ico(str(temp))
    systray.update(icon="icon.ico", hover_text=f"temp at {config["city"]}")

    root.destroy()
    root.mainloop()

    print(config)


def open_weather_gov(systray):
    with open("config.json") as fh:
        config = json.loads(fh.read())
    webbrowser.open(f"https://forecast.weather.gov/MapClick.php?lat={config["lat"]}&lon={config["lon"]}")

def select_text_color(systray):
    with open("config.json") as fh:
        config = json.loads(fh.read())
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    color_code = colorchooser.askcolor(title = "Choose color")
    config["color"] = ",".join([str(c) for c in color_code[0]])
    # write config
    with open("config.json", "w") as fh:
        fh.write(json.dumps(config))
    # update temp
    # get current temp
    response = requests.get(config["url"])
    json_response = json.loads(response.content)
    temp = json_response["properties"]["periods"][0]["temperature"]
    # rewrite ico
    write_ico(str(temp))
    systray.update(icon="icon.ico", hover_text=f"temp at {config["city"]}")

    root.destroy()
    root.mainloop()

write_ico("")
menu_options = (("Open forecast",None,open_weather_gov),("Change location", None, configure_city_state),("Select color",None,select_text_color))
systray = SysTrayIcon(icon="icon.ico", hover_text=f"Temp at {config["city"]}", menu_options=menu_options)
systray.start()

while True:
    # open config
    with open("config.json") as fh:
        config = json.loads(fh.read())

    # get current temp
    response = requests.get(config["url"])
    json_response = json.loads(response.content)
    temp = json_response["properties"]["periods"][0]["temperature"]

    write_ico(str(temp))
    systray.update(icon="icon.ico")

    # sleep for 1 hour
    sleep(3600)