import os
import json
import time
import threading
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment stuff
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not API_KEY:
    print(" Couldn't load API key from .env, double check it.")
    exit()

print("API Key loaded")

# Grab config
try:
    with open("config.json", "r") as f:
        settings = json.load(f)
        CITIES = settings.get("locations", [])
        INTERVAL = settings.get("refresh_interval", 3)
except Exception as config_err:
    print("Error reading config.json:", config_err)
    exit()

# DB setup
mongo = MongoClient("mongodb://localhost:27017/")
db = mongo["weather_db"]
forecast_data = db["forecast"]
map_data = db["weather_maps"]

# forecast pulling #
def get_forecast(city_name):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={API_KEY}&units=imperial"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            result = res.json()
            forecast_data.insert_one({
                "city": city_name,
                "fetched_at": datetime.now(timezone.utc),
                "data": result
            })
            print(f"Forecast saved: {city_name}")

            for entry in result.get("list", []):
                temp = entry["main"].get("temp", 0)
                if temp > 140:
                    continue  # obviously bad data

                weather_tags = [w["main"].lower() for w in entry.get("weather", [])]
                if temp <= 32 or "rain" in weather_tags or "snow" in weather_tags:
                    print(f"  ALERT {city_name} @ {entry['dt_txt']} → {weather_tags} {temp}°F")
        else:
            print(f"[x] Couldn't fetch for {city_name}: {res.status_code}")
    except Exception as boom:
        print(f"[!!] Error for {city_name}: {boom}")


def forecast_loop():
    while True:
        for c in CITIES:
            get_forecast(c)
            time.sleep(60 // len(CITIES))
        time.sleep(INTERVAL * 60)


#map downloader (simulated) #
def save_fake_map(city):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
    sim_url = f"https://dummyimage.com/600x400/000/fff&text=Map+{city}+{ts}"
    try:
        map_data.insert_one({
            "city": city,
            "timestamp": datetime.now(timezone.utc),
            "url": sim_url
        })
        print(f"[Map] {city} map saved.")
    except Exception as err:
        print(f"Map save error: {err}")


def map_loop():
    while True:
        for c in CITIES:
            save_fake_map(c)
            time.sleep(60 // len(CITIES))
        time.sleep(INTERVAL * 60)


if __name__ == "__main__":
    print("⏳ Weather monitor starting...")

    thread1 = threading.Thread(target=forecast_loop)
    thread2 = threading.Thread(target=map_loop)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()