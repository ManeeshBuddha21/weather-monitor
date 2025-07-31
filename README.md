
Smart Weather Monitor

This is a Python weather monitoring dashboard that uses the OpenWeatherMap API. It fetches and displays weather forecasts and maps, saves them to MongoDB, and shows everything on a Tkinter GUI. I built this for a coding challenge using threading, APIs, MongoDB, and basic GUI design.

?What it does

- Uses threads to do multiple tasks at once
- Grabs weather forecast data (5-day / 3-hour)
- Downloads and shows latest weather maps
- Saves forecast and map data to MongoDB
- Detects alerts like rain, snow, or freezing temperatures
- Lets you pick a city from dropdown to view its forecast, map, and alerts
- Shows temp vs time graphs
- Displays countdown to next data refresh

?How I built it

- Python 3
- MongoDB
- OpenWeatherMap API
- Tkinter for UI
- Matplotlib for graphs
- Pillow for image display
- Threads for multitasking

?How to run it

1. Clone the repo
2. Create an OpenWeatherMap account and get your API key
3. Put your API key into the `.env` file (or add directly to code)
4. Install the needed Python libraries:

```
pip install -r requirements.txt
```

5. Make sure MongoDB is running locally
6. Edit `config.json` with the cities you want and how often to refresh(in seconds)

```json
{
  "locations": ["New York", "San Francisco", "Los Angeles"],
  "refresh_interval": 180
}
```

7. Run the app:
```
py main.py
```

?What's in the repo

- `main.py` – Main logic and GUI
- `config.json` – City list + refresh time
- `requirements.txt` – Libraries used
- `weather_maps/` – Where maps are saved
- MongoDB gets two collections: `forecast` and `maps`

Notes

- Doesn’t hit API too frequently (below 60 calls per minute)
- Alerts are auto-detected and shown
- Graph uses the latest data from DB

