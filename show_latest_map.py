import cv2
import requests
import numpy as np
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["weather_db"]
maps_col = db["weather_maps"]

# Change this to any city you want to test
CITY = "Los Angeles"

def show_latest_map(city):
    # Find the latest map for the city
    latest = maps_col.find_one({"city": city}, sort=[("timestamp", -1)])
    if not latest:
        print("No map found for this city yet.")
        return

    # Download image from URL
    image_url = latest["url"]
    response = requests.get(image_url)
    img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img is not None:
        cv2.imshow(f"Weather Map - {city}", img)
        print(f"🖼️ Showing latest map for {city}")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Failed to load image from URL.")

if __name__ == "__main__":
    show_latest_map(CITY)
