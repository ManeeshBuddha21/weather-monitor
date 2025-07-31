from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["weather_db"]
forecast_col = db["weather_forecast"]

test_doc = {
    "city": "Test City",
    "timestamp": datetime.utcnow(),
    "temperature": 77,
    "condition": "Sunny"
}

result = forecast_col.insert_one(test_doc)
print(f"Inserted ID: {result.inserted_id}")
