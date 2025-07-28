
import matplotlib.pyplot as plt
from pymongo import MongoClient
from datetime import datetime

# connect to MongoDB
mongo = MongoClient("mongodb://localhost:27017/")
db = mongo["weather_db"]
forecast_data = db["forecast"]

CITY_NAME = "Los Angeles"

def show_plot(city):
    doc = forecast_data.find_one({"city": city}, sort=[("timestamp", -1)])
    if not doc:
        print("No data found for", city)
        return

    forecast_list = doc.get("data", {}).get("list", [])
    if not forecast_list:
        print("Forecast list empty for", city)
        return

    timestamps = []
    temps = []

    for item in forecast_list:
        try:
            dt = datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S")
            temp = item["main"]["temp"]
            timestamps.append(dt)
            temps.append(temp)
        except Exception as e:
            print("Skip entry:", e)
            continue

    plt.figure(figsize=(12, 5))
    plt.plot(timestamps, temps, color="orange", linestyle="--", marker="o")
    plt.title(f"{city} Temp Forecast (next few days)")
    plt.xlabel("Time")
    plt.ylabel("Temp (°F)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    show_plot(CITY_NAME)
