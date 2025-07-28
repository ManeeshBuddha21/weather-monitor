import matplotlib.pyplot as plt
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["weather_db"]
forecast_col = db["forecast"]

# Change this to your desired city
CITY = "Los Angeles"

def plot_forecast(city):
    # Get latest forecast document
    doc = forecast_col.find_one({"city": city}, sort=[("timestamp", -1)])
    if not doc:
        print("No forecast data found.")
        return

    data = doc["data"]["list"]

    times = [datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S") for item in data]
    temps = [item["main"]["temp"] for item in data]

    plt.figure(figsize=(12, 5))
    plt.plot(times, temps, marker='o', linestyle='-', color='blue')
    plt.title(f"Temperature Forecast for {city}")
    plt.xlabel("Time")
    plt.ylabel("Temperature (°F)")
    plt.grid(True)
    plt.tight_layout()
    plt.xticks(rotation=45)
    plt.show()

if __name__ == "__main__":
    plot_forecast(CITY)
