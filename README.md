# Weather Monitor - Python Project

This is a small project I made for a coding challenge.  
It uses OpenWeatherMap API to get 5-day forecast for some cities.  
I also saved the data into MongoDB, and made alerts and graphs.

## What it does

- Gets weather forecast for multiple cities (every few mins)
- Simulates weather map images (fake map with city + timestamp)
- Saves everything to MongoDB
- If rain, snow, or temp below 32F → prints alert
- Shows a graph of temperature using matplotlib
- Can also display the latest map using OpenCV

## How to run

1. First install the requirements  
bash
pip install -r requirements.txt


2. Then add your OpenWeather API key in `.env` file like this:  

OPENWEATHER_API_KEY=your_key_here


3. In `config.json`, change the cities you want to monitor and refresh time (in minutes):  
json
{
  "locations": ["Los Angeles", "New York"],
  "refresh_interval": 3
}


4. To run the monitor (forecast + maps together):  
bash
python main.py


5. To show the graph:  
bash
python plot_forecast.py


6. To display the latest map image:  
bash
python show_latest_map.py


## Notes

- For now I'm faking the weather maps using dummyimage.com. I added city name and timestamp for each map.
- Forecast is pulled every few mins using threads, so everything runs together

## Files

main.py (runs the whole monitor with 2 threads)
plot_forecast.py (shows the temperature graph)
show_latest_map.py (opens latest map using OpenCV)
config.json (config file for cities and timing)
.env  (API key)
requirements.txt (all libraries needed)
README.md 

Please let me know if any issue running this.
