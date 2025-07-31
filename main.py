

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, UnidentifiedImageError
import requests, threading, time, os, json
from datetime import datetime, timezone
from pymongo import MongoClient
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict

from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")


#MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["weather_db"]
forecast_col = db["forecast"]
maps_col = db["maps"]

#Load Config
with open("config.json", "r") as f:
    config = json.load(f)
LOCATIONS = config["locations"]
REFRESH_INTERVAL = config["refresh_interval"]

#Globals
map_folder = "weather_maps"
thread_status = {k: "idle" for k in ["Forecast", "Map", "Plot", "Viewer"]}
status_colors = {"done": "green", "fetching": "yellow", "error": "red", "idle": "gray"}
status_labels = {}
countdown_seconds = REFRESH_INTERVAL
city_alerts = defaultdict(list)
selected_city = None

#GUI Setup
root = tk.Tk()
root.title("Smart Weather Dashboard")
root.geometry("1200x800")
selected_city = tk.StringVar(value=LOCATIONS[0])

#Thread Status
status_frame = tk.LabelFrame(root, text="Thread Status", padx=10, pady=10)
status_frame.grid(row=0, column=0, columnspan=3, sticky="ew")
for idx, key in enumerate(thread_status):
    lbl = tk.Label(status_frame, text=f"Thread {idx+1} - {key}: Idle", bg=status_colors["idle"], width=30)
    lbl.grid(row=0, column=idx)
    status_labels[key] = lbl

#MongoDB Info
mongo_frame = tk.LabelFrame(root, text="MongoDB Info", padx=10, pady=10)
mongo_frame.grid(row=1, column=0, sticky="nsew")
mongo_text = tk.Text(mongo_frame, height=18, width=35)
mongo_text.pack()

#Forecast Graph
plot_frame = tk.LabelFrame(root, text="Forecast Graph", padx=10, pady=10)
plot_frame.grid(row=1, column=1, sticky="nsew")
tk.Label(plot_frame, text="Select City:").pack()
city_selector = ttk.Combobox(plot_frame, values=LOCATIONS, state="readonly", textvariable=selected_city)
city_selector.pack()
fig = Figure(figsize=(5, 4), dpi=100)
plot = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack()

#Weather Map
map_frame = tk.LabelFrame(root, text="Latest Weather Map", padx=10, pady=10)
map_frame.grid(row=1, column=2, sticky="nsew")
map_label = tk.Label(map_frame)
map_label.pack()

#Weather Alerts
alert_frame = tk.LabelFrame(root, text="Weather Alerts", padx=10, pady=10)
alert_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
alert_scroll = tk.Scrollbar(alert_frame)
alert_scroll.pack(side="right", fill="y")
alert_text = tk.Text(alert_frame, height=8, width=85, yscrollcommand=alert_scroll.set)
alert_text.pack()
alert_scroll.config(command=alert_text.yview)

#Task Summary
task_frame = tk.LabelFrame(root, text="Task Summary", padx=10, pady=10)
task_frame.grid(row=2, column=2, sticky="nsew")
task_text = tk.Text(task_frame, height=6, width=40)
task_text.insert(tk.END, "- Forecast: 5-day/3hr data\n- Map: Weather tile image\n- Plot: Temp vs Time\n- Viewer: Show latest map")
task_text.config(state="disabled")
task_text.pack()

#Bottom block
bottom_frame = tk.Frame(root)
bottom_frame.grid(row=3, column=0, columnspan=3, sticky="ew")
countdown_label = tk.Label(bottom_frame, text="Next refresh in 03:00")
countdown_label.pack(side="left")
last_updated_label = tk.Label(bottom_frame, text="Last updated: Never")
last_updated_label.pack(side="right")

#Thread Status
def update_thread_status(name, status):
    lbl = status_labels[name]
    lbl.config(text=f"{lbl.cget('text').split('-')[0]}- {name}: {status.capitalize()}", bg=status_colors.get(status, "gray"))

# Forecast
def fetch_forecast():
    update_thread_status("Forecast", "fetching")
    try:
        for city in LOCATIONS:
            url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=imperial"
            res = requests.get(url)
            res.raise_for_status()
            data = res.json()
            forecast_col.insert_one({"city": city, "data": data, "timestamp": datetime.now(timezone.utc)})
            new_alerts = []
            for item in data["list"]:
                temp = item["main"]["temp"]
                weather = item["weather"][0]["main"].lower()

                reason = None
                if temp <= 32:
                    reason = "Freezing"
                elif weather == "rain":
                    reason = "Rain"
                elif weather == "snow":
                    reason = "Snow"

                if reason:
                    entry = f"[{city}]  {reason} ({temp:.2f}°F) at {item['dt_txt']}"
                    if entry not in city_alerts[city]:
                        new_alerts.append(entry)
            city_alerts[city].extend(new_alerts)
        update_thread_status("Forecast", "done")
    except Exception as e:
        update_thread_status("Forecast", "error")


#Alerts
def display_alerts():
    city = selected_city.get()
    alert_text.delete(1.0, tk.END)
    if city_alerts[city]:
        for a in sorted(set(city_alerts[city])):
            alert_text.insert(tk.END, a + "\n")
    else:
        alert_text.insert(tk.END, " No alerts for this city")

# Plot 
def plot_forecast():
    update_thread_status("Plot", "fetching")
    try:
        city = selected_city.get()
        data = forecast_col.find_one({"city": city}, sort=[("timestamp", -1)])
        if data:
            temps = [d["main"]["temp"] for d in data["data"]["list"]]
            times = [d["dt_txt"][5:16] for d in data["data"]["list"]]
            plot.clear()
            plot.plot(times, temps, marker='o')
            plot.set_title(f"{city} Forecast")
            plot.tick_params(axis='x', rotation=45)
            plot.set_ylabel("Temp (°F)")
            canvas.draw()
        update_thread_status("Plot", "done")
    except Exception as e:
        update_thread_status("Plot", "error")

#Map Fetch
def fetch_map():
    update_thread_status("Map", "fetching")
    try:
        url = f"https://tile.openweathermap.org/map/clouds_new/0/0/0.png?appid={API_KEY}"
        res = requests.get(url)
        if res.status_code == 200:
            os.makedirs(map_folder, exist_ok=True)
            path = os.path.join(map_folder, f"map_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.png")
            with open(path, "wb") as f:
                f.write(res.content)
            maps_col.insert_one({"timestamp": datetime.now(timezone.utc), "path": path})
        update_thread_status("Map", "done")
    except Exception as e:
        update_thread_status("Map", "error")

#View Map
def view_map():
    update_thread_status("Viewer", "fetching")
    try:
        latest = maps_col.find_one(sort=[("timestamp", -1)])
        if latest and os.path.exists(latest["path"]):
            img = Image.open(latest["path"]).resize((320, 200)).convert("RGB")
            map_img = ImageTk.PhotoImage(img)
            map_label.configure(image=map_img)
            map_label.image = map_img
        else:
            map_label.config(text="No map found")
        update_thread_status("Viewer", "done")
    except UnidentifiedImageError as e:
        update_thread_status("Viewer", "error")

# Mongo Info
def update_mongo_info():
    mongo_text.delete(1.0, tk.END)
    try:
        mongo_text.insert(tk.END, "Fetched:\n")
        mongo_text.insert(tk.END, f" - Forecast for {', '.join(LOCATIONS)}\n - Weather map tiles\n\n")
        mongo_text.insert(tk.END, f" - Forecast entries: {forecast_col.count_documents({})}\n")
        mongo_text.insert(tk.END, f" - Map entries: {maps_col.count_documents({})}\n\n")
        f = forecast_col.find_one(sort=[("timestamp", -1)])
        m = maps_col.find_one(sort=[("timestamp", -1)])
        mongo_text.insert(tk.END, "Latest Writes:\n")
        mongo_text.insert(tk.END, f" - Forecast: {f['timestamp'] if f else 'N/A'}\n")
        mongo_text.insert(tk.END, f" - Map: {m['timestamp'] if m else 'N/A'}")
    except Exception as e:
        mongo_text.insert(tk.END, f"Error loading info: {e}")

#Main Task Runner
def run_all():
    threads = []
    for func in [fetch_forecast, fetch_map, plot_forecast, view_map]:
        t = threading.Thread(target=func)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    update_mongo_info()
    display_alerts()
    last_updated_label.config(text="Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

#Timer(refresh)
def start_timer():
    global countdown_seconds
    mins, secs = divmod(countdown_seconds, 60)
    countdown_label.config(text=f"Next refresh in {mins:02}:{secs:02}")
    if countdown_seconds > 0:
        countdown_seconds -= 1
        root.after(1000, start_timer)
    else:
        countdown_seconds = REFRESH_INTERVAL
        threading.Thread(target=run_all).start()
        root.after(1000, start_timer)

# On City Change
def handle_city(event):
    plot_forecast()
    display_alerts()

# Bind dropdown
city_selector.bind("<<ComboboxSelected>>", handle_city)

# Initial Start
os.makedirs(map_folder, exist_ok=True)
threading.Thread(target=run_all).start()
start_timer()
root.mainloop()