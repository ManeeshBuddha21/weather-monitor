import cv2
import numpy as np
from pymongo import MongoClient
from datetime import datetime

# MongoDB 
mongo = MongoClient("mongodb://localhost:27017/")
db = mongo["weather_db"]
maps_col = db["weather_maps"]

# Pick your city to view map
CITY_NAME = "Los Angeles"

def show_latest_map_for(city):
    # getting latest map entry
    entry = maps_col.find_one({"city": city}, sort=[("timestamp", -1)])
    if not entry:
        print(f"🤷 No maps found for {city}")
        return

    ts = entry["timestamp"].strftime("%Y%m%d%H%M")
    label = f"Weather Map {city} {ts}"

    img = np.zeros((400, 800, 3), dtype=np.uint8)
    cv2.putText(img, label, (50, 220), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)

    window_title = f"Weather Map - {city}"
    cv2.imshow(window_title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    show_latest_map_for(CITY_NAME)
